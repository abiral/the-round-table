"""Sequential turn-taking conversation graph with intake and panel selection.

Flow:
    START
      ↓
    entry_router
      ├─ no discussions, no active_agents → intake
      ├─ active_agents empty, has discussions/user_inputs → panel_select
      └─ active_agents present → router

    intake
      ├─ intake check decides "needs questions" → Marcus asks, pause (END)
      └─ intake check decides "context already there" → panel_select (no pause)

    panel_select → router

    router (Haiku)
      ├─ continue_debate / invite_chirp → speaker → router
      ├─ summarize_and_ask_user → summarize → END (pause)
      └─ conclude → conclude → END
"""
from langgraph.graph import StateGraph, END
from app.state import BrainstormState
from app.agents.moderator import (
    IntakeCheckClassifier,
    IntakeAgent,
    PanelSelectAgent,
    ModeratorOpenAgent,  # noqa: F401 -- kept for legacy callers, not used in graph
    ModeratorSummaryAgent,
    ModeratorConcludeAgent,
)
from app.agents.ai_architect import MayaAgent
from app.agents.fullstack import EthanAgent
from app.agents.qa import LenaAgent
from app.agents.ml_scientist import PriyaAgent
from app.agents.php_plugin import SantoshAgent
from app.agents.php_theme import ShreyaAgent
from app.agents.wp_theme_reviewer import RakeshAgent
from app.agents.wp_plugin_reviewer import SuvashAgent
from app.agents.ux_engineer import PremAgent
from app.orchestrator.router import Router


# ── Singletons ─────────────────────────────────────────────────────────────
_intake_check = IntakeCheckClassifier()
_intake_agent = IntakeAgent()
_panel_select = PanelSelectAgent()
_moderator_summary = ModeratorSummaryAgent()
_moderator_conclude = ModeratorConcludeAgent()
_router = Router()

AGENT_REGISTRY: dict[str, object] = {
    "nirajan_sharma":    MayaAgent(),
    "samriddhi_neupane": EthanAgent(),
    "prakriti_bhandari": LenaAgent(),
    "aayush_koirala":    PriyaAgent(),
    "santosh_poudel":    SantoshAgent(),
    "shreya_manandhar":  ShreyaAgent(),
    "rakesh_tandulkar":  RakeshAgent(),
    "suvash_bk":         SuvashAgent(),
    "prem_nepali":       PremAgent(),
}

MAX_TURNS = 16


# ── Node functions ─────────────────────────────────────────────────────────

async def intake_node(state: BrainstormState) -> dict:
    """Cheap classifier first. If context is already there, skip ahead silently."""
    problem = state.get("user_goal", "")
    needs = await _intake_check.needs_intake(problem)
    if not needs:
        # Nothing to do here; the conditional edge will route to panel_select.
        return {}
    # Marcus asks intake questions and pauses the session.
    return await _intake_agent.run(state)


async def panel_select_node(state: BrainstormState) -> dict:
    return await _panel_select.run(state)


async def router_node(state: BrainstormState) -> dict:
    turn_count = state.get("turn_count", 0)
    if turn_count >= MAX_TURNS:
        return {
            "next_action": "conclude",
            "next_speaker": None,
            "next_mode": "full",
            "last_router_reason": "max turn budget reached",
        }

    decision = await _router.decide(state)

    callback = state.get("stream_callback")
    if callback:
        await callback({
            "type": "router_decision",
            "action": decision["action"],
            "next_speaker": decision["next_speaker"],
            "reason": decision["reason"],
        })

    return {
        "next_action": decision["action"],
        "next_speaker": decision["next_speaker"],
        "next_mode": decision["mode"],
        "last_router_reason": decision["reason"],
    }


async def speaker_node(state: BrainstormState) -> dict:
    agent_key = state.get("next_speaker")
    if not agent_key or agent_key not in AGENT_REGISTRY:
        return {"turn_count": state.get("turn_count", 0) + 1}

    agent = AGENT_REGISTRY[agent_key]
    mode = state.get("next_mode") or "full"
    result = await agent.run(state, mode=mode)

    return {
        **result,
        "turn_count": state.get("turn_count", 0) + 1,
        "next_speaker": None,
        "next_action": "",
        "last_router_reason": "",
    }


async def summarize_node(state: BrainstormState) -> dict:
    return await _moderator_summary.run(state)


async def conclude_node(state: BrainstormState) -> dict:
    return await _moderator_conclude.run(state)


# ── Edge routing ───────────────────────────────────────────────────────────

def entry_router(state: BrainstormState) -> str:
    """First-call routing.

    1) No panel selected yet and no transcript: run intake to ask the user about stack / LLM.
    2) No panel selected but transcript exists (intake answered, OR intake was skipped on resume): pick the panel.
    3) Panel already selected: hand off to the router for the normal turn loop.
    """
    active = state.get("active_agents") or []
    discussions = state.get("discussions") or []
    user_inputs = state.get("user_inputs") or []

    if not active and not discussions and not user_inputs:
        return "intake"
    if not active:
        return "panel_select"
    return "router"


def route_after_intake(state: BrainstormState) -> str:
    """If intake paused for the user, end. Otherwise go straight to panel_select."""
    if state.get("awaiting_user_input"):
        return "__end__"
    return "panel_select"


def route_after_router(state: BrainstormState) -> str:
    action = state.get("next_action") or "continue_debate"
    if action == "summarize_and_ask_user":
        return "summarize"
    if action == "conclude":
        return "conclude"
    return "speaker"


# ── Graph construction ─────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(BrainstormState)

    g.add_node("intake", intake_node)
    g.add_node("panel_select", panel_select_node)
    g.add_node("router", router_node)
    g.add_node("speaker", speaker_node)
    g.add_node("summarize", summarize_node)
    g.add_node("conclude", conclude_node)

    g.set_conditional_entry_point(entry_router, {
        "intake": "intake",
        "panel_select": "panel_select",
        "router": "router",
    })

    g.add_conditional_edges("intake", route_after_intake, {
        "panel_select": "panel_select",
        "__end__": END,
    })

    g.add_edge("panel_select", "router")

    g.add_conditional_edges("router", route_after_router, {
        "speaker": "speaker",
        "summarize": "summarize",
        "conclude": "conclude",
    })

    g.add_edge("speaker", "router")
    g.add_edge("summarize", END)
    g.add_edge("conclude", END)

    return g.compile()


brainstorm_graph = build_graph()
