"""FastAPI entrypoint.

Conversations are persisted to Postgres via app.conversations.store. The SSE
generator opens its own DB session inside the background task because the
request-scoped session has already closed by the time the graph finishes.
"""
import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

from app.agents.documentation import nora_agent
from app.agents.title import generate_title
from app.auth.deps import current_user
from app.auth.routes import router as auth_router
from app.conversations import store
from app.conversations.routes import router as conversations_router
from app.db.session import async_session_maker, get_session
from app.exports.pdf_report import render_pdf
from app.models.user import User
from app.orchestrator.graph import brainstorm_graph
from app.state import BrainstormState

from sqlalchemy.ext.asyncio import AsyncSession


app = FastAPI(title="AI Brainstorming Agent", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(conversations_router)


# ── Request bodies ────────────────────────────────────────────────────────

class BrainstormRequest(BaseModel):
    problem: str
    constraints: list[str] = []


class RespondRequest(BaseModel):
    content: str


# ── SSE helper ────────────────────────────────────────────────────────────

_DONE = object()


def _initial_state(problem: str, constraints: list[str], session_id: str) -> BrainstormState:
    return {
        "user_goal": problem,
        "constraints": constraints,
        "session_id": session_id,
        "turn_count": 0,
        "last_speaker": None,
        "next_speaker": None,
        "next_mode": "full",
        "next_action": "",
        "last_router_reason": "",
        "awaiting_user_input": False,
        "pause_summary": "",
        "pause_question": "",
        "conversation_concluded": False,
        "final_summary": "",
        "discussions": [],
        "user_inputs": [],
        "risks": [],
        "decisions": [],
        "unresolved_questions": [],
        "exports": {},
    }


def _state_for_resume(prev: BrainstormState, user_content: str) -> BrainstormState:
    user_msg = {
        "role": "user",
        "content": user_content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    # Append, do NOT replace. LangGraph's operator.add reducer only kicks in
    # for in-graph node returns, not for the initial state we hand to astream,
    # so we have to carry the full cumulative list ourselves.
    prior_inputs = list(prev.get("user_inputs") or [])
    return {
        **prev,
        "awaiting_user_input": False,
        "pause_summary": "",
        "pause_question": "",
        "next_speaker": None,
        "next_action": "",
        "next_mode": "full",
        "last_router_reason": "",
        "user_inputs": [*prior_inputs, user_msg],
    }


def _uuid_from(value: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


async def _stream_graph(
    initial_state: BrainstormState,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    existing_title: str = "",
):
    """Run the graph and yield SSE events.

    Uses `astream(stream_mode="values")` so we hold the latest full-state
    snapshot after every node. On any exit path (success, LLM error,
    cancellation) we persist that snapshot to Postgres, so a mid-stream
    failure leaves the conversation in a recoverable state for /retry.
    """
    queue: asyncio.Queue = asyncio.Queue()

    async def stream_callback(event: dict):
        await queue.put(event)

    initial_state = {**initial_state, "stream_callback": stream_callback}
    final_state_holder: dict = {}

    async def run_graph():
        try:
            async for snapshot in brainstorm_graph.astream(
                initial_state, stream_mode="values"
            ):
                # Each yield is the full state after a node. Keep overwriting
                # so the holder always carries the latest one we have seen.
                final_state_holder["state"] = snapshot
        except Exception as exc:
            await queue.put({"type": "error", "message": str(exc)})

        # Always try to persist whatever progress we have, even on error.
        final = final_state_holder.get("state")
        if final is not None:
            try:
                title = existing_title
                if not title:
                    title = await generate_title(final.get("user_goal", ""))
                async with async_session_maker() as db:
                    await store.save_state(
                        db,
                        conversation_id=conversation_id,
                        user_id=user_id,
                        state=final,
                        title=title or None,
                    )
            except Exception:
                # Saving must not crash the SSE generator.
                pass

        await queue.put(_DONE)

    task = asyncio.create_task(run_graph())

    # First event: announce the conversation id. Field name stays `session_id`
    # for backwards compatibility with existing frontend types; the value is
    # the conversation UUID.
    yield f"data: {json.dumps({'type': 'session', 'session_id': str(conversation_id)})}\n\n"

    while True:
        event = await queue.get()
        if event is _DONE:
            break
        yield f"data: {json.dumps(event)}\n\n"

    try:
        await task
    except Exception:
        pass

    final_state: BrainstormState | None = final_state_holder.get("state")
    if final_state is not None:
        if final_state.get("awaiting_user_input"):
            yield "data: " + json.dumps({
                "type": "awaiting_user_input",
                "summary": final_state.get("pause_summary", ""),
                "question": final_state.get("pause_question", ""),
            }) + "\n\n"
        elif final_state.get("conversation_concluded"):
            yield "data: " + json.dumps({
                "type": "conclude_offered",
                "summary": final_state.get("final_summary", ""),
                "exports_available": ["pdf", "adr", "plan"],
            }) + "\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


# ── Endpoints ─────────────────────────────────────────────────────────────

@app.post("/api/brainstorm")
async def brainstorm(
    request: BrainstormRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    conversation_id = uuid.uuid4()
    state = _initial_state(request.problem, request.constraints, str(conversation_id))

    # Pre-create the conversation row so the user has a recoverable record even
    # if the SSE stream is interrupted before the first save. The SSE generator
    # will overwrite this with the post-graph state.
    await store.save_state(
        db,
        conversation_id=conversation_id,
        user_id=user.id,
        state=state,
        title="",
    )

    return StreamingResponse(
        _stream_graph(state, conversation_id, user.id, existing_title=""),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.post("/api/brainstorm/{conversation_id}/retry")
async def retry(
    conversation_id: str,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """Re-invoke the graph from the saved state without adding any user input.

    Used when a previous round errored or the SSE stream was interrupted: the
    user can resume from the last successful snapshot.
    """
    cid = _uuid_from(conversation_id)
    row = await store.load(db, conversation_id=cid, user_id=user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    state = {
        **(row.state or {}),
        # Clear ephemeral routing fields so the router picks fresh.
        "next_speaker": None,
        "next_action": "",
        "next_mode": "full",
        "last_router_reason": "",
    }

    return StreamingResponse(
        _stream_graph(state, cid, user.id, existing_title=row.title or ""),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.post("/api/brainstorm/{conversation_id}/respond")
async def respond(
    conversation_id: str,
    request: RespondRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    cid = _uuid_from(conversation_id)
    row = await store.load(db, conversation_id=cid, user_id=user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    state = _state_for_resume(row.state or {}, request.content)

    return StreamingResponse(
        _stream_graph(state, cid, user.id, existing_title=row.title or ""),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/brainstorm/{conversation_id}/export/{kind}")
async def export(
    conversation_id: str,
    kind: str,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    cid = _uuid_from(conversation_id)
    row = await store.load(db, conversation_id=cid, user_id=user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if kind not in ("pdf", "adr", "plan"):
        raise HTTPException(status_code=400, detail="Unknown export kind")

    state: dict = row.state or {}
    exports = dict(state.get("exports") or {})

    if kind == "pdf":
        report_md = exports.get("report_md")
        if report_md is None:
            report_md = await nora_agent.generate_report(state)
            exports["report_md"] = report_md
        # PDF bytes are NOT persisted (they don't fit in JSONB). Always render
        # fresh; the markdown cache above keeps the cost down on repeated clicks.
        pdf_bytes = render_pdf(state, report_md)

        # Persist the regenerated report_md back to the row so future calls skip
        # the LLM (we still skip persisting the bytes themselves).
        await store.save_state(
            db,
            conversation_id=cid,
            user_id=user.id,
            state={**state, "exports": exports},
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="brainstorm-report.pdf"'},
        )

    if kind == "adr":
        cached = exports.get("adr")
        if cached is None:
            cached = await nora_agent.generate_adr(state)
            exports["adr"] = cached
            await store.save_state(
                db,
                conversation_id=cid,
                user_id=user.id,
                state={**state, "exports": exports},
            )
        return Response(
            content=cached,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="decision-record.md"'},
        )

    # kind == "plan"
    cached = exports.get("plan")
    if cached is None:
        cached = await nora_agent.generate_plan_md(state)
        exports["plan"] = cached
        await store.save_state(
            db,
            conversation_id=cid,
            user_id=user.id,
            state={**state, "exports": exports},
        )
    return Response(
        content=cached,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="plan.md"'},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
