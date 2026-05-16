import os
from langchain_core.language_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

ANTHROPIC_MODEL = "claude-sonnet-4-6"
ANTHROPIC_FAST_MODEL = "claude-haiku-4-5"
GEMINI_MODEL = "gemini-2.0-flash"


def get_llm(preferred: str = "anthropic", *, fast: bool = False) -> BaseChatModel:
    """
    Return an LLM client.

    fast=True forces Anthropic Haiku (cheap + fast). Use it for routing,
    classification, and other lightweight calls. The preferred provider
    is ignored in fast mode because Haiku is the cheapest path.
    """
    if fast:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Set it in backend/.env or export it before starting the server."
            )
        return ChatAnthropic(
            model=ANTHROPIC_FAST_MODEL,
            max_tokens=512,
        )

    if preferred == "gemini" and os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            max_output_tokens=1024,
        )

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. "
            "Set it in backend/.env or export it before starting the server."
        )
    return ChatAnthropic(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
    )


def active_provider(preferred: str = "anthropic") -> str:
    """Return which provider will actually be used (for logging/display)."""
    if preferred == "gemini" and os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    return "anthropic"
