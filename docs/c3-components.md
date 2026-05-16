[← C2 — Containers](c2-containers.md) | **C3 — Components** | [C4 — Code →](c4-code.md)

---

# C3 — Components

> **C4 Level 3:** Zooms into individual containers and shows the internal components and their relationships.

---

## Backend Components

```
backend/app/
│
├── main.py                  ← FastAPI app + SSE endpoint
│     │
│     └── calls ──────────────────────────────────────────┐
│                                                         │
├── orchestrator/                                         │
│   └── graph.py             ← LangGraph StateGraph       │
│         │                                               │
│         ├── moderator_node ──────────────────────────┐  │
│         ├── expert_node (×N, parallel via Send) ──┐  │  │
│         ├── critic_node                           │  │  │
│         └── synthesizer_node                     │  │  │
│                                                  │  │  │
├── agents/                                        │  │  │
│   ├── base.py              ← BaseAgent           │  │  │
│   │     └── uses providers.py                   │  │  │
│   ├── moderator.py         ← Saugat Adhikari ────────┘  │  │
│   ├── ai_architect.py      ← Nirajan Sharma ─────────────┘  │
│   ├── fullstack.py         ← Samriddhi Neupane              │
│   ├── qa.py                ← Prakriti Bhandari               │
│   └── ml_scientist.py      ← Aayush Koirala               │
│                                                         │
├── providers.py             ← LLM factory                │
├── state.py                 ← BrainstormState TypedDict  │
└── prompts/                                              │
    └── personas.py          ← System prompts            ◀┘
```

### `main.py` — FastAPI App + SSE Endpoint

Receives the user's problem via `POST /api/brainstorm` and returns `text/event-stream`. Uses an `asyncio.Queue` to bridge LangGraph's async execution with the streaming HTTP response.

```
Request in
    ↓
_stream_brainstorm() generator
    ↓
asyncio.create_task(run_graph())   ← runs graph in background
    ↓
while True: queue.get()            ← yields SSE events as they arrive
    ↓
StreamingResponse(text/event-stream)
```

---

### `orchestrator/graph.py` — LangGraph StateGraph

Defines the WAT workflow as a compiled `StateGraph`. The critical routing function `route_to_experts` uses the LangGraph `Send` API to dispatch one task per selected agent in parallel.

```
moderator_node
    │
    └── route_to_experts() → [Send("expert_node", state + agent_key), ...]
                                    │
                          expert_node × N  (parallel)
                                    │
                             critic_node
                                    │
                           synthesizer_node
                                    │
                                   END
```

**State accumulation:** Fields written by parallel `expert_node` calls use `Annotated[list, operator.add]` so results are merged, not overwritten.

---

### `agents/base.py` — BaseAgent

Abstract base class all agents extend. Handles LLM instantiation, context building, streaming, and state output.

| Method | Responsibility |
|---|---|
| `__init__` | Calls `get_llm(preferred_provider)` from `providers.py` |
| `_build_context(state)` | Constructs the prompt from goal, constraints, prior discussions |
| `run(state)` | Streams tokens via `llm.astream()`, calls `stream_callback` per token |

---

### `providers.py` — LLM Factory

Centralises provider selection. Checks for `GOOGLE_API_KEY` at runtime.

| Preferred | `GOOGLE_API_KEY` set? | Result |
|---|---|---|
| `"gemini"` | Yes | `ChatGoogleGenerativeAI(gemini-2.0-flash)` |
| `"gemini"` | No | `ChatAnthropic(claude-sonnet-4-6)` (silent fallback) |
| `"anthropic"` | Any | `ChatAnthropic(claude-sonnet-4-6)` |
| Either | `ANTHROPIC_API_KEY` missing | `RuntimeError` |

---

### `state.py` — BrainstormState

Single source of truth for the entire workflow. Fields with `Annotated[list, operator.add]` are parallel-safe; others are single-writer.

| Field | Writer | Reducer |
|---|---|---|
| `user_goal`, `constraints` | Set at invocation | — |
| `active_agents` | `moderator_node` | — |
| `discussions` | All `expert_node` calls | `operator.add` |
| `risks`, `decisions`, `unresolved_questions` | All `expert_node` calls | `operator.add` |
| `contradictions` | `critic_node` | — |
| `consensus_score`, `final_synthesis` | `synthesizer_node` | — |
| `stream_callback` | Injected by `main.py` | — |

---

## Frontend Components

```
frontend/src/
│
├── App.tsx                  ← Root: layout + wires hook to UI
│
├── hooks/
│   └── useBrainstorm.ts     ← SSE stream parser + React state manager
│
├── components/chat/
│   ├── ChatWindow.tsx        ← Scrollable message list + loading dots
│   ├── MessageBubble.tsx     ← User / agent / synthesis bubble variants
│   ├── AgentBadge.tsx        ← Avatar, name, role, provider pill
│   ├── InputBar.tsx          ← Auto-resize textarea + send/stop button
│   └── MarkdownContent.tsx   ← react-markdown wrapper with Tailwind renderers
│
├── types/index.ts            ← StreamEvent, AgentMessage, AGENT_CONFIG
└── lib/utils.ts              ← cn() Tailwind merge utility
```

### `useBrainstorm.ts` — SSE Hook

Owns all streaming logic. Exposes `{ session, submitProblem, cancel }`.

```
submitProblem(problem)
    │
    ├── fetch POST /api/brainstorm
    │
    └── ReadableStream loop
          │
          ├── agent_start  → addAgentMessage()   (new streaming bubble)
          ├── agent_chunk  → appendChunk()        (append token to bubble)
          ├── agent_done   → finishAgent()         (stop cursor)
          ├── done         → set consensusScore, isRunning=false
          └── error        → set error, isRunning=false
```

Uses `AbortController` to cancel in-flight requests.

---

### `MessageBubble.tsx`

Renders three visual variants based on `message.agent` and `message.role`:

| Condition | Variant |
|---|---|
| `agent === 'user'` | Right-aligned blue bubble, plain text |
| `role === 'synthesizer'` | Full-width purple/blue gradient card, markdown |
| Otherwise | Left-aligned white card with `AgentBadge`, markdown |

---

### `MarkdownContent.tsx`

Wraps `react-markdown` with `remark-gfm`. Custom Tailwind renderers for headings, lists, inline/block code, blockquotes, links. Appends a blinking cursor while `isStreaming` is true.

---

[← C2 — Containers](c2-containers.md) | **C3 — Components** | [C4 — Code →](c4-code.md)
