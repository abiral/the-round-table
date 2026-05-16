"""Marcus Vale variants (Saugat Adhikari)."""
import re
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.base import BaseAgent
from app.providers import get_llm
from app.prompts.personas import (
    INTAKE_CHECK_PROMPT,
    MARCUS_INTAKE_PROMPT,
    MARCUS_PANEL_SELECT_PROMPT,
    MARCUS_MODERATOR_PROMPT,
    MARCUS_SUMMARY_PROMPT,
    MARCUS_CONCLUDE_PROMPT,
)
from app.state import BrainstormState


MODERATOR_NAME = "Saugat Adhikari"

VALID_AGENT_IDS = {
    "nirajan_sharma",
    "samriddhi_neupane",
    "prakriti_bhandari",
    "aayush_koirala",
    "santosh_poudel",
    "shreya_manandhar",
    "rakesh_tandulkar",
    "suvash_bk",
    "prem_nepali",
}


# ── Lightweight intake-needed check (Haiku) ────────────────────────────────

class IntakeCheckClassifier:
    """Cheap binary classifier: does the user's problem already contain stack + LLM context?"""

    def __init__(self) -> None:
        self.llm = get_llm("anthropic", fast=True)

    async def needs_intake(self, problem: str) -> bool:
        result = await self.llm.ainvoke([
            SystemMessage(content=INTAKE_CHECK_PROMPT),
            HumanMessage(content=problem),
        ])
        raw = (result.content if isinstance(result.content, str) else str(result.content)).strip()
        # Default to needing intake if the model is ambiguous.
        return "HAS_CONTEXT" not in raw.upper()


# ── Intake (Marcus asks clarifying questions) ─────────────────────────────

class IntakeAgent(BaseAgent):
    name = MODERATOR_NAME
    role = "intake"
    system_prompt = MARCUS_INTAKE_PROMPT

    async def run(self, state: BrainstormState, mode: str = "full") -> dict:
        result = await super().run(state, mode=mode)
        content = result["discussions"][0]["content"]

        match = re.search(r"QUESTION_TO_USER:\s*(.+)", content)
        question = match.group(1).strip() if match else "Could you share your tech stack and which AI providers you have access to?"
        summary_text = re.sub(r"QUESTION_TO_USER:.*", "", content).strip()

        return {
            **result,
            "awaiting_user_input": True,
            "pause_summary": summary_text,
            "pause_question": question,
        }


# ── Panel select (Marcus picks the panel + opens the discussion) ──────────

class PanelSelectAgent(BaseAgent):
    name = MODERATOR_NAME
    role = "moderator"
    system_prompt = MARCUS_PANEL_SELECT_PROMPT

    async def run(self, state: BrainstormState, mode: str = "full") -> dict:
        result = await super().run(state, mode=mode)
        content = result["discussions"][0]["content"]

        match = re.search(r"SELECTED_AGENTS:\s*(.+)", content)
        if match:
            raw = [a.strip() for a in match.group(1).split(",")]
            active = [a for a in raw if a in VALID_AGENT_IDS]
        else:
            active = []

        # Safety fallback: if Marcus picked nothing valid, use the original 4-expert panel.
        if not active:
            active = ["nirajan_sharma", "samriddhi_neupane", "prakriti_bhandari", "aayush_koirala"]

        return {**result, "active_agents": active}


# ── Moderator open (used when intake is skipped and panel is pre-picked) ──

class ModeratorOpenAgent(BaseAgent):
    name = MODERATOR_NAME
    role = "moderator"
    system_prompt = MARCUS_MODERATOR_PROMPT


# ── Summary + Conclude (unchanged behavior) ───────────────────────────────

class ModeratorSummaryAgent(BaseAgent):
    name = MODERATOR_NAME
    role = "summary"
    system_prompt = MARCUS_SUMMARY_PROMPT

    async def run(self, state: BrainstormState, mode: str = "full") -> dict:
        result = await super().run(state, mode=mode)
        content = result["discussions"][0]["content"]

        match = re.search(r"QUESTION_TO_USER:\s*(.+)", content)
        question = match.group(1).strip() if match else "What would you like to explore further?"
        summary_text = re.sub(r"QUESTION_TO_USER:.*", "", content).strip()

        return {
            **result,
            "awaiting_user_input": True,
            "pause_summary": summary_text,
            "pause_question": question,
        }


class ModeratorConcludeAgent(BaseAgent):
    name = MODERATOR_NAME
    role = "conclude"
    system_prompt = MARCUS_CONCLUDE_PROMPT

    async def run(self, state: BrainstormState, mode: str = "full") -> dict:
        result = await super().run(state, mode=mode)
        content = result["discussions"][0]["content"]
        return {
            **result,
            "conversation_concluded": True,
            "final_summary": content,
        }
