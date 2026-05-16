[← C3 — Components](c3-components.md) | **C4 — Code** | [Personas →](personas.md)

---

# C4 — Code

> **C4 Level 4:** The most detailed view. Key interfaces, data structures, and patterns that are non-obvious from reading the code directly.

---

## WAT Pattern

**W**orkflow · **A**gent · **T**ool

| Layer | Implementation | File |
|---|---|---|
| **Workflow** | `StateGraph` — defines the execution graph, edges, and reducers | `orchestrator/graph.py` |
| **Agent** | `BaseAgent` subclasses — each persona is a stateless node | `agents/*.py` |
| **Tool** | LLM inference via LangChain (Phase 2: web search via Tavily) | `providers.py` |

The workflow layer does not contain business logic — it only routes. Business logic (prompting, context building, parsing) lives in the agent layer.

---

## BrainstormState

```python
class BrainstormState(TypedDict):
    # ── Input ────────────────────────────────
    user_goal: str
    constraints: list[str]

    # ── Orchestration ────────────────────────
    active_agents: list[str]           # populated by moderator node

    # ── Parallel-safe (fan-out) ──────────────
    discussions: Annotated[list[AgentDiscussion], operator.add]
    risks:       Annotated[list[str], operator.add]
    decisions:   Annotated[list[str], operator.add]
    unresolved_questions: Annotated[list[str], operator.add]

    # ── Single-writer ────────────────────────
    contradictions:  list[str]         # critic node only
    consensus_score: float             # synthesizer node only
    final_synthesis: str               # synthesizer node only

    # ── Runtime-injected ─────────────────────
    stream_callback: object            # async callable, not serialised
```

`Annotated[list, operator.add]` is the critical pattern for parallel fan-out: when multiple `expert_node` tasks write to the same field concurrently, LangGraph merges by concatenation rather than last-write-wins.

---

## LangGraph Fan-Out (Send API)

```python
def route_to_experts(state: BrainstormState) -> list[Send]:
    return [
        Send("expert_node", {**state, "_agent_key": agent_key})
        for agent_key in state["active_agents"]
    ]

async def expert_node(state: BrainstormState) -> dict:
    agent_key = state.get("_agent_key") or state["active_agents"][0]
    return await AGENT_REGISTRY[agent_key].run(state)
```

`Send("expert_node", state_override)` creates one parallel invocation per agent. Each receives a copy of the full state plus `_agent_key`. LangGraph runs them concurrently (bounded by the event loop) and merges their return values using the reducers before `critic_node` runs.

---

## SSE Streaming Bridge

The core challenge: LangGraph is async but not a generator. The `asyncio.Queue` pattern bridges it cleanly:

```python
async def _stream_brainstorm(problem, constraints):
    queue = asyncio.Queue()
    DONE = object()                            # sentinel

    async def stream_callback(event: dict):    # called by agents
        await queue.put(event)

    async def run_graph():                     # background task
        try:
            await brainstorm_graph.ainvoke({
                ...,
                "stream_callback": stream_callback,
            })
        finally:
            await queue.put(DONE)

    asyncio.create_task(run_graph())           # start graph

    while True:                                # yield SSE events
        event = await queue.get()
        if event is DONE:
            break
        yield f"data: {json.dumps(event)}\n\n"
```

The `yield` makes this an async generator, which FastAPI's `StreamingResponse` consumes directly.

---

## SSE Event Schema

All events are `data: <json>\n\n` lines on the stream.

```typescript
// Frontend type
interface StreamEvent {
  type: 'agent_start' | 'agent_chunk' | 'agent_done' | 'done' | 'error'
  agent?:           string               // agent display name
  role?:            string               // moderator | ai_architect | ...
  provider?:        'anthropic' | 'gemini'
  content?:         string               // token chunk (agent_chunk only)
  consensus_score?: number               // 0.0–1.0 (done only)
  message?:         string               // error description (error only)
}
```

Example stream for a two-agent session:

```
data: {"type":"agent_start","agent":"Saugat Adhikari","role":"moderator","provider":"anthropic"}
data: {"type":"agent_chunk","agent":"Saugat Adhikari","content":"Analyzing"}
data: {"type":"agent_chunk","agent":"Saugat Adhikari","content":" your problem..."}
data: {"type":"agent_done","agent":"Saugat Adhikari"}
data: {"type":"agent_start","agent":"Nirajan Sharma","role":"ai_architect","provider":"gemini"}
data: {"type":"agent_chunk","agent":"Nirajan Sharma","content":"## Architecture\n\n"}
...
data: {"type":"agent_done","agent":"Nirajan Sharma"}
...
data: {"type":"done","consensus_score":0.82}
```

---

## Provider Selection Logic

```python
def get_llm(preferred: str = "anthropic") -> BaseChatModel:
    if preferred == "gemini" and os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", max_output_tokens=1024)

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    return ChatAnthropic(model="claude-sonnet-4-6", max_tokens=1024)
```

Provider resolution happens once at `BaseAgent.__init__` (server startup). Agents are singletons in `AGENT_REGISTRY` so the provider is resolved once per process.

---

## Agent Context Window Budget

Each agent receives only:
1. The original `user_goal` and `constraints`
2. Prior discussions truncated to **600 characters each** (not the full content)

This prevents context window blowout in long sessions and keeps costs predictable. The synthesizer receives full discussions since it needs to integrate all perspectives.

```python
def _build_context(self, state: BrainstormState) -> str:
    prior = "\n".join(
        f"[{d['agent']}]:\n{d['content'][:600]}"   # ← truncation
        for d in state.get("discussions", [])
    )
    ...
```

---

## Key File Map

| File | Role |
|---|---|
| `backend/app/state.py` | Contract — every node reads and writes this shape |
| `backend/app/providers.py` | Single place to add new LLM providers |
| `backend/app/agents/base.py` | Change streaming behaviour here, affects all agents |
| `backend/app/orchestrator/graph.py` | Change the workflow topology here |
| `backend/app/prompts/personas.py` | Change agent personalities here |
| `frontend/src/hooks/useBrainstorm.ts` | Change SSE parsing or React state shape here |
| `frontend/src/components/chat/MarkdownContent.tsx` | Change markdown rendering here |

---

[← C3 — Components](c3-components.md) | **C4 — Code** | [Personas →](personas.md)
