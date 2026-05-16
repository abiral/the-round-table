"""Conversation persistence: load / save / list / delete.

The full BrainstormState is stored in the `state` JSONB column. Before saving
we strip two things:
  - `stream_callback` (a coroutine reference, not JSON-serializable)
  - `state["exports"]["pdf"]` (raw bytes from ReportLab; the PDF is
    deterministic from `state + report_md` so we regenerate on demand)

Status is derived from the state flags so the listing query never has to load
the state blob to determine "in_progress vs awaiting_user vs concluded".
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


def derive_status(state: dict[str, Any]) -> str:
    if state.get("conversation_concluded"):
        return "concluded"
    if state.get("awaiting_user_input"):
        return "awaiting_user"
    return "in_progress"


def sanitize_state_for_persist(state: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-ish copy of `state` safe to JSON-encode."""
    cleaned = {k: v for k, v in state.items() if k != "stream_callback"}
    exports = cleaned.get("exports") or {}
    if exports:
        # Drop only the bytes-valued PDF cache; keep the markdown caches.
        cleaned_exports = {k: v for k, v in exports.items() if k != "pdf"}
        cleaned = {**cleaned, "exports": cleaned_exports}
    # Shallow-copy nested mutable containers so callers cannot accidentally
    # mutate the persisted view via the returned dict.
    return copy.deepcopy(cleaned)


async def save_state(
    db: AsyncSession,
    *,
    conversation_id: Optional[UUID],
    user_id: UUID,
    state: dict[str, Any],
    title: Optional[str] = None,
) -> Conversation:
    """Upsert a conversation by id (insert if id is None or not found)."""
    payload = sanitize_state_for_persist(state)
    status = derive_status(state)
    now = datetime.now(timezone.utc)

    if conversation_id is not None:
        result = await db.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .values(
                state=payload,
                status=status,
                last_message_at=now,
                updated_at=now,
                **({"title": title} if title else {}),
            )
            .returning(Conversation)
        )
        row = result.scalar_one_or_none()
        if row is not None:
            await db.commit()
            return row
        # Fall through to insert with the supplied id.

    new = Conversation(
        id=conversation_id,
        user_id=user_id,
        title=title or "",
        status=status,
        state=payload,
        last_message_at=now,
    )
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new


async def load(
    db: AsyncSession, *, conversation_id: UUID, user_id: UUID
) -> Optional[Conversation]:
    return (
        await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
    ).scalar_one_or_none()


async def list_for_user(db: AsyncSession, *, user_id: UUID) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.last_message_at.desc())
    )
    return list(result.scalars().all())


async def delete_for_user(
    db: AsyncSession, *, conversation_id: UUID, user_id: UUID
) -> bool:
    result = await db.execute(
        delete(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    await db.commit()
    return (result.rowcount or 0) > 0
