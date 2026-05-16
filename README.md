# The RoundTable
A multi-agent AI brainstorming platform where a team of expert AI personas collaboratively analyze and solve technical problems in real time.

Built with **LangGraph** (WAT pattern), **FastAPI**, and **React + Shadcn/ui**.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Documentation (C4 Model)](#documentation-c4-model)
  - [C1 — System Context](docs/c1-system-context.md)
  - [C2 — Containers](docs/c2-containers.md)
  - [C3 — Components](docs/c3-components.md)
  - [C4 — Code](docs/c4-code.md)
  - [Personas](docs/personas.md)
  - [Getting Started](docs/getting-started.md)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)

---

## How It Works

You describe a technical problem. A moderator agent selects the most relevant expert personas, each one contributes their perspective in parallel, a critic detects contradictions, and a synthesizer produces a final recommendation — all streamed token-by-token to the chat UI.

---

## Documentation (C4 Model)

This project is documented following the [C4 model](https://c4model.com) — four levels of increasing detail.

| Level | File | Description |
|---|---|---|
| C1 | [System Context](docs/c1-system-context.md) | How the system fits into the world |
| C2 | [Containers](docs/c2-containers.md) | Frontend, backend, and external services |
| C3 | [Components](docs/c3-components.md) | Internal structure of each container |
| C4 | [Code](docs/c4-code.md) | Key interfaces, state, and patterns |

### Additional Docs

- [Personas](docs/personas.md) — The 5 expert AI personas and their domains
- [Getting Started](docs/getting-started.md) — Setup and running the project

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Shadcn/ui |
| Backend | Python 3.11+, FastAPI, LangGraph |
| LLM (primary) | Anthropic Claude (`claude-sonnet-4-6`) |
| LLM (optional) | Google Gemini (`gemini-2.0-flash`) |
| Streaming | Server-Sent Events (SSE) |
| Agent pattern | WAT — Workflow · Agent · Tool |

---

## Quick Start

### Option A: Run locally (no docker)

```bash
# Backend
cd backend
cp .env.example .env     # add your ANTHROPIC_API_KEY
uv run uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
cp .env.example .env     # VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

### Option B: Run via docker compose

The compose stack starts Postgres, Redis, the backend, and the frontend together.
Host-side ports are env-driven so it can run alongside a local Postgres / Redis
without clashes (default Postgres on **5433**, default Redis on **6380**).

```bash
cp .env.example .env             # adjust ports here if needed
cp backend/.env.example backend/.env   # add ANTHROPIC_API_KEY (re-used by docker)
docker compose up --build
```

Then open [http://localhost:5173](http://localhost:5173) (or your `FRONTEND_PORT`).

To stop and remove containers:

```bash
docker compose down              # keep volumes
docker compose down -v           # also wipe postgres / redis data
```

Switch between modes freely. Postgres data on the host is isolated from
Postgres data in docker (different volumes / data dirs), so neither setup
disturbs the other.

See [Getting Started](docs/getting-started.md) for full setup instructions.
