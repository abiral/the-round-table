[← C1 — System Context](c1-system-context.md) | **C2 — Containers** | [C3 — Components →](c3-components.md)

---

# C2 — Containers

> **C4 Level 2:** Zooms into the system boundary and shows the high-level technical building blocks (containers) and how they communicate.

---

## Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        AI Brainstorming Board                            │
│                                                                          │
│  ┌─────────────────────────────────┐                                     │
│  │         React Frontend          │                                     │
│  │                                 │                                     │
│  │  • Vite + TypeScript            │                                     │
│  │  • Tailwind CSS + Shadcn/ui     │                                     │
│  │  • useBrainstorm() SSE hook     │                                     │
│  │  • Markdown rendering           │                                     │
│  │                                 │                                     │
│  │  Served on: localhost:5173      │                                     │
│  └──────────────┬──────────────────┘                                     │
│                 │                                                        │
│                 │  POST /api/brainstorm                                  │
│                 │  Response: text/event-stream (SSE)                     │
│                 │                                                        │
│  ┌──────────────▼──────────────────┐    ┌──────────────────────────────┐│
│  │         FastAPI Backend         │    │    LangGraph Orchestrator    ││
│  │                                 │    │                              ││
│  │  • Python 3.11+                 │    │  • StateGraph (WAT pattern)  ││
│  │  • SSE streaming endpoint       │───▶│  • Moderator node            ││
│  │  • asyncio.Queue bridge         │    │  • Expert nodes (fan-out)    ││
│  │  • CORS middleware              │    │  • Critic node               ││
│  │  • Provider factory             │    │  • Synthesizer node          ││
│  │                                 │◀───│  • stream_callback           ││
│  │  Served on: localhost:8000      │    │                              ││
│  └─────────────────────────────────┘    └──────────────────────────────┘│
│                 │                                                        │
└─────────────────┼────────────────────────────────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
┌───────────────┐   ┌────────────────┐
│   Anthropic   │   │ Google Gemini  │
│  Claude API   │   │      API       │
│               │   │   (optional)   │
└───────────────┘   └────────────────┘
```

---

## Containers

### React Frontend
**Technology:** React 18, TypeScript, Vite 5, Tailwind CSS 3, Shadcn/ui

The single-page application users interact with. Renders a full-height chat interface where agent messages appear and stream in real time.

**Key responsibilities:**
- Render a streaming chat UI (user messages, per-agent bubbles, synthesis card)
- Consume the SSE stream from the backend using `fetch()` + `ReadableStream`
- Parse and display markdown in agent responses
- Show which LLM provider each agent is using (Claude / Gemini pill)
- Display a consensus score on session completion

**Configuration:** `frontend/.env` → `VITE_API_BASE_URL`

---

### FastAPI Backend
**Technology:** Python 3.11+, FastAPI, uvicorn, python-dotenv

The HTTP server that accepts brainstorm requests and bridges LangGraph execution to the SSE response stream.

**Key responsibilities:**
- Expose `POST /api/brainstorm` returning `text/event-stream`
- Inject a `stream_callback` into the LangGraph state
- Bridge LangGraph output to the HTTP response via `asyncio.Queue`
- Configure CORS for the frontend origin

**Configuration:** `backend/.env` → `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `CORS_ORIGINS`

---

### LangGraph Orchestrator
**Technology:** LangGraph, langchain-anthropic, langchain-google-genai

The multi-agent workflow engine. Implements the WAT (Workflow · Agent · Tool) pattern as a `StateGraph`.

**Key responsibilities:**
- Run the moderator to select which agents are relevant
- Fan-out to expert agents in parallel via the `Send` API
- Accumulate discussions using `operator.add` reducers (parallel-safe)
- Run the critic to surface contradictions
- Run the synthesizer to produce the final recommendation

**Pattern:** Four nodes — `moderator → expert_node (×N, parallel) → critic → synthesizer → END`

---

## Communication

| From | To | Protocol | Description |
|---|---|---|---|
| Browser | FastAPI | HTTP POST + SSE | Submit problem, receive event stream |
| FastAPI | LangGraph | Python in-process | Invoke graph, pass stream callback |
| LangGraph agents | Anthropic API | HTTPS | LLM inference, streaming |
| LangGraph agents | Gemini API | HTTPS | LLM inference, streaming (optional) |
| LangGraph nodes | FastAPI | asyncio.Queue | Push SSE events as they are generated |

---

[← C1 — System Context](c1-system-context.md) | **C2 — Containers** | [C3 — Components →](c3-components.md)
