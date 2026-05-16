# CLAUDE.md

Project-level instructions for Claude Code working in this repository.

---

## What This Project Is

A multi-agent AI brainstorming platform. Users submit a technical problem; a LangGraph orchestrator routes it through 5 expert AI personas, streams their responses via SSE, and synthesizes a final recommendation.

**Pattern:** WAT — Workflow (LangGraph StateGraph) · Agent (persona nodes) · Tool (LLM providers)

---

## How to Run

```bash
# Backend — from /backend
uv run uvicorn app.main:app --reload --port 8000

# Frontend — from /frontend
npm run dev
```

Both must be running for the full system to work. See [docs/getting-started.md](docs/getting-started.md) for env setup.

---

## Repository Layout

```
backend/app/
  main.py            # FastAPI entry point + SSE endpoint
  state.py           # BrainstormState TypedDict — the workflow contract
  providers.py       # LLM factory: Anthropic / Gemini with fallback logic
  agents/
    base.py          # BaseAgent: streaming, context building, state output
    moderator.py     # Saugat Adhikari — always runs (moderator + synthesizer)
    ai_architect.py  # Nirajan Sharma (Gemini preferred)
    fullstack.py     # Samriddhi Neupane (Gemini preferred)
    qa.py            # Prakriti Bhandari (Claude)
    ml_scientist.py  # Aayush Koirala (Gemini preferred)
  orchestrator/
    graph.py         # LangGraph StateGraph — the WAT workflow
  prompts/
    personas.py      # System prompts for all 5 personas

frontend/src/
  hooks/useBrainstorm.ts           # SSE stream parser + React state
  components/chat/
    ChatWindow.tsx                 # Scrollable message list
    MessageBubble.tsx              # Three bubble variants (user/agent/synthesis)
    AgentBadge.tsx                 # Avatar + name + role + provider pill
    InputBar.tsx                   # Textarea + send/stop button
    MarkdownContent.tsx            # react-markdown with Tailwind renderers
  types/index.ts                   # StreamEvent, AgentMessage, AGENT_CONFIG
```

---

## Key Architectural Rules

### Backend

- **Agents are stateless.** No agent stores state between calls. All shared state lives in `BrainstormState`.
- **Parallel fan-out is safe** only for fields annotated with `Annotated[list, operator.add]`. Never write single-writer fields (`final_synthesis`, `consensus_score`, `contradictions`) from `expert_node`.
- **Provider selection happens at startup.** `BaseAgent.__init__` calls `get_llm()` once. AGENT_REGISTRY singletons are created at import time — the server must have API keys set before it starts.
- **All streaming goes through `stream_callback`.** Never yield directly from a node. Always use the queue bridge in `main.py`.
- **Context is truncated per agent** at 600 characters per prior discussion to control token cost.

### Frontend

- **`useBrainstorm` owns all SSE state.** Components are purely presentational — they receive props only.
- **`VITE_API_BASE_URL` must be set** in `frontend/.env`. The Vite proxy uses it in dev; the hook uses it directly in prod.
- **Agent colors and initials** are configured in `AGENT_CONFIG` in `types/index.ts`. Add new agents there when adding new personas.
- **User messages are plain text.** Only agent messages go through `MarkdownContent`.

---

## Adding a New Agent

1. Add a system prompt constant to `backend/app/prompts/personas.py`
2. Create `backend/app/agents/<name>.py` extending `BaseAgent` — set `name`, `role`, `system_prompt`, and optionally `preferred_provider`
3. Register the agent in `AGENT_REGISTRY` in `backend/app/orchestrator/graph.py`
4. Add color config to `AGENT_CONFIG` in `frontend/src/types/index.ts`

---

## Adding a New LLM Provider

1. Install the LangChain integration package (`uv add langchain-<provider>`)
2. Add detection logic to `backend/app/providers.py` — follow the existing `if preferred == "gemini" and os.getenv(...)` pattern
3. Add the key to `backend/.env.example`
4. Set `preferred_provider = "<name>"` on the relevant agent classes

---

## Environment Variables

| File | Variable | Required | Purpose |
|---|---|---|---|
| `backend/.env` | `ANTHROPIC_API_KEY` | Yes | Primary LLM for all agents |
| `backend/.env` | `GOOGLE_API_KEY` | No | Enables Gemini for Maya, Ethan, Priya |
| `backend/.env` | `CORS_ORIGINS` | No | Allowed frontend origins |
| `frontend/.env` | `VITE_API_BASE_URL` | Yes | Backend base URL |

---

## Documentation

Full C4-model documentation lives in [docs/](docs/):

- [docs/c1-system-context.md](docs/c1-system-context.md) — actors and external systems
- [docs/c2-containers.md](docs/c2-containers.md) — frontend, backend, orchestrator
- [docs/c3-components.md](docs/c3-components.md) — internal components and their relationships
- [docs/c4-code.md](docs/c4-code.md) — key patterns, state shape, SSE schema
- [docs/personas.md](docs/personas.md) — all 5 expert personas and their domains
- [docs/getting-started.md](docs/getting-started.md) — setup and running
