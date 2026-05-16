"""LLM-based turn router.

Runs on Haiku (cheap + fast). Decides who speaks next, when to pause, when to conclude.
The set of valid next-speakers is provided by state["active_agents"], so the router
honors the dynamic panel the moderator picked.
"""
import json
import re
from typing import Literal, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
from app.providers import get_llm
from app.prompts.personas import ROUTER_PROMPT
from app.state import BrainstormState


# Display info for each known agent ID. Kept in sync with AGENT_REGISTRY.
AGENT_INFO: dict[str, tuple[str, str]] = {
    "nirajan_sharma":    ("Nirajan Sharma", "AI Systems Architect"),
    "samriddhi_neupane": ("Samriddhi Neupane", "Senior Full Stack Engineer"),
    "prakriti_bhandari": ("Prakriti Bhandari", "QA & Reliability Engineer"),
    "aayush_koirala":    ("Aayush Koirala", "ML Scientist"),
    "santosh_poudel":    ("Santosh Poudel", "PHP & WordPress Plugin Developer"),
    "shreya_manandhar":  ("Shreya Manandhar", "PHP & WordPress Theme Developer"),
    "rakesh_tandulkar":  ("Rakesh Tandulkar", "WordPress Theme Reviewer"),
    "suvash_bk":         ("Suvash BK", "WordPress Plugin Reviewer"),
    "prem_nepali":       ("Prem Nepali", "UI / UX Engineer"),
}


Action = Literal[
    "continue_debate",
    "invite_chirp",
    "summarize_and_ask_user",
    "conclude",
]


class RouterDecision(TypedDict):
    action: Action
    next_speaker: str | None
    mode: Literal["full", "chirp"]
    reason: str


def _build_context(state: BrainstormState) -> str:
    active = state.get("active_agents") or []
    panel_lines = []
    for aid in active:
        info = AGENT_INFO.get(aid)
        if info:
            panel_lines.append(f"- {aid}: {info[0]} ({info[1]})")
        else:
            panel_lines.append(f"- {aid}")
    panel_block = "\n".join(panel_lines) if panel_lines else "(no panel set)"

    discussions = state.get("discussions", [])
    user_inputs = state.get("user_inputs", [])

    merged: list[tuple[str, dict]] = (
        [(d["timestamp"], {"kind": "agent", **d}) for d in discussions]
        + [(u["timestamp"], {"kind": "user", **u}) for u in user_inputs]
    )
    merged.sort(key=lambda x: x[0])

    lines: list[str] = []
    for _, item in merged:
        if item["kind"] == "user":
            lines.append(f"[USER]: {item['content'][:400]}")
        else:
            chirp_tag = " (chirp)" if item.get("is_chirp") else ""
            lines.append(
                f"[{item.get('agent')} - {item.get('role')}{chirp_tag}]: "
                f"{item.get('content', '')[:400]}"
            )

    turn_count = state.get("turn_count", 0)
    last_speaker = state.get("last_speaker") or "none"
    spoke_counts: dict[str, int] = {}
    for d in discussions:
        spoke_counts[d.get("agent", "?")] = spoke_counts.get(d.get("agent", "?"), 0) + 1
    spoke_summary = ", ".join(f"{k}: {v}" for k, v in spoke_counts.items()) or "no one yet"

    return (
        f"Problem: {state.get('user_goal', '')}\n"
        f"Panel (these are the ONLY valid next_speaker IDs):\n{panel_block}\n\n"
        f"Turn count: {turn_count}\n"
        f"Last speaker: {last_speaker}\n"
        f"Speaker tally: {spoke_summary}\n\n"
        f"Recent transcript:\n" + ("\n".join(lines[-12:]) if lines else "(empty)")
    )


def _parse_decision(raw: str, panel: list[str]) -> RouterDecision:
    cleaned = raw.strip()
    fence = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(0)

    try:
        data = json.loads(cleaned)
    except Exception:
        return RouterDecision(
            action="continue_debate",
            next_speaker=panel[0] if panel else None,
            mode="full",
            reason="router parse fallback",
        )

    action = data.get("action") or "continue_debate"
    if action not in ("continue_debate", "invite_chirp", "summarize_and_ask_user", "conclude"):
        action = "continue_debate"

    next_speaker = data.get("next_speaker")
    if action in ("summarize_and_ask_user", "conclude"):
        next_speaker = None
    elif next_speaker not in panel:
        next_speaker = panel[0] if panel else None

    mode = data.get("mode") or ("chirp" if action == "invite_chirp" else "full")
    if mode not in ("full", "chirp"):
        mode = "full"

    reason = str(data.get("reason") or "").strip()[:240]

    return RouterDecision(
        action=action,
        next_speaker=next_speaker,
        mode=mode,
        reason=reason,
    )


class Router:
    def __init__(self) -> None:
        self.llm = get_llm("anthropic", fast=True)

    async def decide(self, state: BrainstormState) -> RouterDecision:
        context = _build_context(state)
        messages = [
            SystemMessage(content=ROUTER_PROMPT),
            HumanMessage(content=context),
        ]
        result = await self.llm.ainvoke(messages)
        raw = result.content if isinstance(result.content, str) else str(result.content)
        return _parse_decision(raw, state.get("active_agents") or [])
