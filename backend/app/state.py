from typing import TypedDict, Annotated, Literal, Optional
import operator


class AgentDiscussion(TypedDict, total=False):
    agent: str
    role: str
    content: str
    timestamp: str
    is_chirp: bool


class UserInput(TypedDict):
    role: Literal["user"]
    content: str
    timestamp: str


class BrainstormState(TypedDict, total=False):
    # ── Input ─────────────────────────────────────────────────────────────
    user_goal: str
    constraints: list[str]

    # ── Session ──────────────────────────────────────────────────────────
    session_id: str

    # ── Panel composition (single-writer, set by panel_select) ───────────
    active_agents: list[str]

    # ── Turn-taking control (single-writer, set by router) ───────────────
    turn_count: int
    last_speaker: Optional[str]
    next_speaker: Optional[str]
    next_mode: Literal["full", "chirp"]
    next_action: Literal[
        "continue_debate",
        "invite_chirp",
        "summarize_and_ask_user",
        "conclude",
        "",
    ]
    last_router_reason: str

    # ── Pause / conclude flags (terminal signals) ────────────────────────
    awaiting_user_input: bool
    pause_summary: str
    pause_question: str
    conversation_concluded: bool
    final_summary: str

    # ── Parallel-safe accumulators ───────────────────────────────────────
    discussions: Annotated[list[AgentDiscussion], operator.add]
    user_inputs: Annotated[list[UserInput], operator.add]
    risks: Annotated[list[str], operator.add]
    decisions: Annotated[list[str], operator.add]
    unresolved_questions: Annotated[list[str], operator.add]

    # ── Cached export artifacts (not part of streaming flow) ─────────────
    exports: dict

    # ── Async callback injected at runtime — not persisted ───────────────
    stream_callback: object
