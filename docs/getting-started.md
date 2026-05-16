[← Back to README](../README.md) | **Getting Started** | [C1 — System Context →](c1-system-context.md)

---

# Getting Started

## Prerequisites

| Tool | Minimum version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| uv | latest (`curl -LsSf https://astral.sh/uv/install.sh \| sh`) |
| npm | 8+ |

---

## 1. Clone and explore

```bash
git clone <repo-url>
cd brainstroming-agent
```

---

## 2. Backend setup

```bash
cd backend

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
```

Edit `backend/.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...          # required
GOOGLE_API_KEY=AIza...                # optional — enables Gemini for Maya, Ethan, Priya
CORS_ORIGINS=http://localhost:5173    # adjust if frontend runs on a different port
```

Start the backend:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Verify it is running:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
```

Edit `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

## 4. Test the SSE stream directly

```bash
curl -N -X POST http://localhost:8000/api/brainstorm \
  -H 'Content-Type: application/json' \
  -d '{"problem": "Should we use a monorepo or separate repos for a new AI product?"}'
```

You should see a stream of `data: {...}` events — one per token from each agent.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key. Used by all agents when Gemini is unavailable. |
| `GOOGLE_API_KEY` | No | Google AI Studio key. Enables Gemini for Maya, Ethan, and Priya. |
| `CORS_ORIGINS` | No | Comma-separated allowed origins. Default: `http://localhost:5173` |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | Yes | Base URL of the FastAPI backend. Default: `http://localhost:8000` |

---

## Project Structure

```
brainstroming-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + SSE endpoint
│   │   ├── state.py             # BrainstormState TypedDict
│   │   ├── providers.py         # LLM factory (Anthropic / Gemini)
│   │   ├── agents/              # One file per persona
│   │   ├── orchestrator/        # LangGraph StateGraph
│   │   └── prompts/             # System prompts
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── hooks/               # useBrainstorm SSE hook
│   │   ├── components/chat/     # Chat UI components
│   │   └── types/               # TypeScript interfaces
│   └── package.json
├── docs/                        # C4 documentation
├── refs/                        # Original architecture references
├── README.md
└── CLAUDE.md
```

---

## Adding a New Agent (Phase 2)

1. Add a system prompt to `backend/app/prompts/personas.py`
2. Create `backend/app/agents/<name>.py` extending `BaseAgent`
3. Register it in `AGENT_REGISTRY` in `backend/app/orchestrator/graph.py`
4. Add the agent's color config to `AGENT_CONFIG` in `frontend/src/types/index.ts`

That is all — the moderator will start selecting it automatically when relevant.

---

[← Back to README](../README.md) | **Getting Started** | [C1 — System Context →](c1-system-context.md)
