"""Haiku-backed conversation title generator.

One LLM call per session, fired on the first save when `title == ''`. Cheap
(small prompt + ~30-token output) and the result is human-friendly for the
sidebar. Falls back to a truncated problem statement on any failure.
"""
from __future__ import annotations

import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.providers import get_llm


TITLE_SYSTEM_PROMPT = """You write short titles for a list view.
You will be given a brainstorming problem.
Return a 4 to 8 word title that captures what the conversation is about.
Title case. No quotes. No trailing punctuation. No em dashes.
Output ONLY the title."""


_llm = None


def _get() -> object:
    global _llm
    if _llm is None:
        _llm = get_llm("anthropic", fast=True)
    return _llm


def _fallback(problem: str) -> str:
    problem = (problem or "").strip()
    if not problem:
        return "Untitled brainstorm"
    if len(problem) <= 60:
        return problem
    return problem[:60].rsplit(" ", 1)[0] + "…"


def _sanitize(title: str) -> str:
    title = title.strip().strip('"').strip("'").strip(".")
    # Strip em / en dashes per the project style rule.
    title = title.replace("—", ",").replace("–", ",")
    # Collapse repeated whitespace.
    title = re.sub(r"\s+", " ", title)
    # Hard length safeguard.
    if len(title) > 80:
        title = title[:80].rsplit(" ", 1)[0]
    return title


async def generate_title(problem: str) -> str:
    if not (problem or "").strip():
        return _fallback(problem)
    try:
        result = await _get().ainvoke(
            [
                SystemMessage(content=TITLE_SYSTEM_PROMPT),
                HumanMessage(content=problem.strip()),
            ]
        )
        raw = result.content if isinstance(result.content, str) else str(result.content)
        title = _sanitize(raw)
        return title or _fallback(problem)
    except Exception:
        return _fallback(problem)
