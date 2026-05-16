[← Getting Started](getting-started.md) | **C1 — System Context** | [C2 — Containers →](c2-containers.md)

---

# C1 — System Context

> **C4 Level 1:** Shows the system as a single box and how it interacts with users and external systems.

---

## Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Systems                         │
│                                                                 │
│   ┌───────────────────────┐   ┌────────────────────────────┐   │
│   │   Anthropic Claude    │   │     Google Gemini API      │   │
│   │  (claude-sonnet-4-6)  │   │    (gemini-2.0-flash)      │   │
│   │                       │   │                            │   │
│   │  Primary LLM for all  │   │  Optional LLM for Maya,   │   │
│   │  agents by default    │   │  Ethan, and Priya agents  │   │
│   └───────────┬───────────┘   └──────────────┬─────────────┘   │
│               │                              │                  │
└───────────────┼──────────────────────────────┼──────────────────┘
                │                              │
                └──────────────┬───────────────┘
                               │ HTTPS / API calls
                               ▼
              ┌────────────────────────────────┐
              │                                │
              │      AI Brainstorming Board    │
              │                                │
              │  Multi-agent system that lets  │
              │  users brainstorm technical    │
              │  problems with AI experts      │
              │                                │
              └────────────────┬───────────────┘
                               │ Browser (HTTP + SSE)
                               ▼
                    ┌──────────────────────┐
                    │       User           │
                    │                     │
                    │  A developer,       │
                    │  architect, or      │
                    │  technical lead     │
                    │  with a problem     │
                    │  to solve           │
                    └──────────────────────┘
```

---

## Actors

### User
A technical professional (engineer, architect, product manager) who wants to explore a technical problem from multiple expert angles simultaneously.

**Goals:**
- Get structured, multi-perspective analysis of a technical decision
- Surface contradictions and risks they may not have considered
- Receive a synthesized recommendation they can act on

### AI Brainstorming Board
The system being documented. Orchestrates a team of AI expert personas through a LangGraph workflow and streams their responses to the user in real time.

**Responsibilities:**
- Accept a problem statement from the user
- Select relevant expert agents for the problem
- Run agents and stream their output
- Detect contradictions between agents
- Synthesize a final recommendation with a consensus score

### Anthropic Claude API
The primary LLM provider. Used by all agents unless overridden.

- Model: `claude-sonnet-4-6`
- Used by: Saugat Adhikari, Prakriti Bhandari (always), and any agent whose preferred provider is unavailable

### Google Gemini API
An optional secondary LLM provider. Activated only when `GOOGLE_API_KEY` is set.

- Model: `gemini-2.0-flash`
- Used by: Nirajan Sharma, Samriddhi Neupane, Aayush Koirala (when key is present)
- Falls back to Anthropic silently when key is absent

---

[← Getting Started](getting-started.md) | **C1 — System Context** | [C2 — Containers →](c2-containers.md)
