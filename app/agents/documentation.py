"""Nora Patel — Technical Writer & Documentation Lead.

Non-streaming utility agent. Used only by export endpoints to turn the conversation
transcript into ADR and plan.md artifacts. Does NOT appear in the chat.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from app.providers import get_llm
from app.prompts.personas import NORA_PATEL_PROMPT
from app.state import BrainstormState


def _build_transcript(state: BrainstormState, char_cap: int = 1500) -> str:
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
            lines.append(f"### User\n{item['content'][:char_cap]}")
        else:
            chirp_tag = " (chirp-in)" if item.get("is_chirp") else ""
            lines.append(
                f"### {item.get('agent')} — {item.get('role')}{chirp_tag}\n"
                f"{item.get('content', '')[:char_cap]}"
            )

    return "\n\n".join(lines)


ADR_PROMPT_TEMPLATE = """The following is a transcript of a multi-expert brainstorming session.

Problem: {problem}
Constraints: {constraints}

Transcript:
{transcript}

Final moderator summary:
{final_summary}

Produce an Architecture Decision Record using the MADR template. Use this exact markdown structure:

# ADR: <short title derived from the problem>

- **Status:** Proposed
- **Date:** {date}

## Context and Problem Statement
<2–4 sentences. What is the problem? What is the forcing function?>

## Decision Drivers
- <driver 1>
- <driver 2>
- <driver 3>

## Considered Options
- <option 1>
- <option 2>
- <option 3 if applicable>

## Decision Outcome
**Chosen option:** "<the option the room converged on>", because <one-sentence reason>.

### Positive Consequences
- <consequence 1>
- <consequence 2>

### Negative Consequences / Risks
- <risk 1>
- <risk 2>

## Pros and Cons of the Options

### <option 1>
- ✅ <pro>
- ❌ <con>

### <option 2>
- ✅ <pro>
- ❌ <con>

## Open Questions
- <unresolved question 1>
- <unresolved question 2>

Return ONLY the markdown ADR. Do not wrap it in a code fence. Do not add commentary."""


REPORT_PROMPT_TEMPLATE = """The following is the transcript of a multi-expert brainstorming session.

Problem: {problem}
Constraints: {constraints}

Transcript (do NOT echo this back verbatim; synthesize it):
{transcript}

Final moderator summary:
{final_summary}

Produce a structured decision report in markdown with these EXACT sections, in this order:

# <Title>
(A short title derived from the problem, 5 to 10 words. No "ADR:" prefix.)

## Problem
(2 to 4 sentences. State the problem and the context that matters. Include the stack and constraints the user provided.)

## Recommended Solution
(3 to 6 sentences describing the recommended approach. Be concrete and decisive. This is the "what we are going to do" section.)

## How We Arrived at This
(A short narrative, 3 to 5 sentences. Describe the path the panel took to reach the recommendation. Refer to participants by ROLE only: "the AI Architect", "the Plugin Reviewer", "the UX Engineer", "the moderator". Never use personal names. Mention where the discussion turned, where there was disagreement, and how it was resolved.)

## Parameters Considered
(Bullet list of 4 to 8 factors the panel weighed. Each bullet should name the factor and briefly summarize how it was resolved. Examples:
- Latency vs. cost: chose Haiku for routing because the decisions are short and do not need a frontier model.
- Plugin store compliance: required, because the user plans to submit to WP.org.)

## Key Decisions
(Short bullet list. Each bullet is a concrete decision the room agreed on.)

## Open Risks and Questions
(Short bullet list. Things that remain unresolved or worth tracking.)

Rules:
- Refer to participants by ROLE only, never by personal name.
- Never use em dashes (—) or en dashes (–). Use commas, periods, or parentheses.
- Output markdown only. No code fence. No preamble. No closing remark.
"""


PLAN_PROMPT_TEMPLATE = """The following is a transcript of a multi-expert brainstorming session.

Problem: {problem}
Constraints: {constraints}

Transcript:
{transcript}

Final moderator summary:
{final_summary}

Produce an editor-ready plan.md document that an AI coding agent (Claude Code, Cursor, etc.)
can use to execute on this work. Use this exact markdown structure:

# Plan: <short title>

## Context
<3–5 sentences explaining why this change is being made, what prompted it, the intended outcome.>

## Goals
- <goal 1>
- <goal 2>

## Non-Goals
- <thing this plan deliberately does NOT cover>

## Approach
<A few paragraphs describing the recommended approach at a level a senior engineer can execute.>

## Critical Files
- `<path>` — <what to change>
- `<path>` — <what to change>

(If specific paths weren't discussed, leave them as placeholders like `<TBD: backend/path/to/module>` — do not invent file paths.)

## Risks
- <risk 1>
- <risk 2>

## Verification
1. <how to test step 1>
2. <how to test step 2>

## Out of Scope
- <items deliberately deferred>

Return ONLY the markdown plan. Do not wrap it in a code fence. Do not add commentary."""


class NoraDocumentationAgent:
    """Non-streaming. One LLM call per artifact."""

    name = "Nora Patel"
    role = "documentation"

    def __init__(self) -> None:
        self.llm = get_llm("anthropic")

    async def _run_prompt(self, prompt: str) -> str:
        messages = [
            SystemMessage(content=NORA_PATEL_PROMPT),
            HumanMessage(content=prompt),
        ]
        result = await self.llm.ainvoke(messages)
        return result.content if isinstance(result.content, str) else str(result.content)

    def _common_fields(self, state: BrainstormState) -> dict:
        from datetime import date
        return {
            "problem": state.get("user_goal", ""),
            "constraints": ", ".join(state.get("constraints", []) or []) or "None specified",
            "transcript": _build_transcript(state),
            "final_summary": state.get("final_summary", "") or "(session was paused, not concluded)",
            "date": date.today().isoformat(),
        }

    async def generate_adr(self, state: BrainstormState) -> str:
        return await self._run_prompt(ADR_PROMPT_TEMPLATE.format(**self._common_fields(state)))

    async def generate_plan_md(self, state: BrainstormState) -> str:
        return await self._run_prompt(PLAN_PROMPT_TEMPLATE.format(**self._common_fields(state)))

    async def generate_report(self, state: BrainstormState) -> str:
        """Decision report combining ADR-style structure with synthesized rationale.

        Used as the markdown body of the PDF export. The PDF rendering layer
        appends a role-only discussion trail after this content.
        """
        return await self._run_prompt(REPORT_PROMPT_TEMPLATE.format(**self._common_fields(state)))


nora_agent = NoraDocumentationAgent()
