from langchain_core.messages import SystemMessage, HumanMessage
from app.state import BrainstormState, AgentDiscussion
from app.providers import get_llm, active_provider
from datetime import datetime, timezone


class BaseAgent:
    name: str
    role: str
    system_prompt: str
    preferred_provider: str = "anthropic"

    def __init__(self):
        self.llm = get_llm(self.preferred_provider)
        self.provider = active_provider(self.preferred_provider)

    def _build_context(self, state: BrainstormState, mode: str = "full") -> str:
        """Build the human-message context including prior turns + user replies inline."""
        turns: list[str] = []
        discussions = state.get("discussions", [])
        user_inputs = state.get("user_inputs", [])

        # Weave user inputs into the timeline by timestamp so the agent sees the real flow.
        merged: list[tuple[str, dict]] = (
            [(d["timestamp"], {"kind": "agent", **d}) for d in discussions]
            + [(u["timestamp"], {"kind": "user", **u}) for u in user_inputs]
        )
        merged.sort(key=lambda x: x[0])

        for _, item in merged:
            if item["kind"] == "user":
                turns.append(f"[USER]:\n{item['content'][:600]}")
            else:
                tag = f"[{item.get('agent')} — {item.get('role')}"
                if item.get("is_chirp"):
                    tag += " · chirp"
                tag += "]"
                turns.append(f"{tag}:\n{item.get('content', '')[:600]}")

        constraints = ", ".join(state.get("constraints", [])) or "None specified"
        prior = "\n\n".join(turns) if turns else "None yet — you are speaking first."

        router_hint = ""
        reason = state.get("last_router_reason", "")
        if reason:
            router_hint = f"\n\nModerator's note to you: {reason}"

        mode_hint = ""
        if mode == "chirp":
            mode_hint = (
                "\n\nThis is a CHIRP-IN, not a full turn. "
                "Keep your reply to 1–2 sentences — a short reaction or quick add. "
                "Do not restate prior arguments. Stay in character."
            )
        else:
            mode_hint = (
                "\n\nSpeak in your own voice and stay in character. "
                "If you disagree with a prior speaker, name them and explain why. "
                "If a prior speaker challenged YOUR earlier point, defend or refine it. "
                "Keep it conversational (3–6 short paragraphs at most)."
            )

        return (
            f"Problem: {state['user_goal']}\n"
            f"Constraints: {constraints}\n\n"
            f"Conversation so far:\n{prior}"
            f"{router_hint}{mode_hint}"
        )

    async def run(self, state: BrainstormState, mode: str = "full") -> dict:
        callback = state.get("stream_callback")
        context = self._build_context(state, mode=mode)
        is_chirp = mode == "chirp"

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=context),
        ]

        if callback:
            await callback({
                "type": "agent_start",
                "agent": self.name,
                "role": self.role,
                "provider": self.provider,
                "chirp": is_chirp,
            })

        full_content = ""
        async for chunk in self.llm.astream(messages):
            token = chunk.content if isinstance(chunk.content, str) else ""
            if token:
                full_content += token
                if callback:
                    await callback({
                        "type": "agent_chunk",
                        "agent": self.name,
                        "content": token,
                    })

        if callback:
            await callback({"type": "agent_done", "agent": self.name})

        discussion: AgentDiscussion = {
            "agent": self.name,
            "role": self.role,
            "content": full_content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_chirp": is_chirp,
        }

        return {
            "discussions": [discussion],
            "last_speaker": self.name,
        }
