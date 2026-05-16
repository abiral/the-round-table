"""Conversation list / detail / delete endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user
from app.conversations import store
from app.conversations.schemas import ConversationDetail, ConversationListItem
from app.db.session import get_session
from app.models.user import User


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _parse_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except (ValueError, TypeError):
        # Don't 422 here; we want 404 to match the cross-user policy.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.get("", response_model=list[ConversationListItem])
async def list_conversations(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    rows = await store.list_for_user(db, user_id=user.id)
    return [
        ConversationListItem(
            id=str(r.id),
            title=r.title or _fallback_title(r.state),
            status=r.status,  # type: ignore[arg-type]
            last_message_at=r.last_message_at,
        )
        for r in rows
    ]


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    cid = _parse_uuid(conversation_id)
    row = await store.load(db, conversation_id=cid, user_id=user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ConversationDetail(
        id=str(row.id),
        title=row.title or _fallback_title(row.state),
        status=row.status,  # type: ignore[arg-type]
        last_message_at=row.last_message_at,
        state=row.state or {},
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    cid = _parse_uuid(conversation_id)
    await store.delete_for_user(db, conversation_id=cid, user_id=user.id)
    # Idempotent: deleting an unknown id still returns ok so we don't leak existence.
    return {"status": "ok"}


def _fallback_title(state: dict) -> str:
    goal = (state.get("user_goal") or "").strip()
    if not goal:
        return "Untitled brainstorm"
    if len(goal) <= 60:
        return goal
    cut = goal[:60].rsplit(" ", 1)[0]
    return f"{cut}…"
