
# AI Brainstorming System Implementation Plan

## Goal
Build a multi-agent AI brainstorming platform using LangGraph, NestJS, React, PostgreSQL, and Redis.

---

# Recommended Architecture

```txt
Frontend (React)
    ↓
NestJS API Gateway
    ↓
LangGraph Orchestrator
    ↓
Expert Agents
    ↓
Critic / Validator Agents
    ↓
Synthesizer
    ↓
Final Response
```

---

# Tech Stack

## Frontend
- React
- TypeScript
- Vite
- Zustand or Redux
- TailwindCSS

## Backend
- NestJS
- TypeScript
- LangGraph
- LangChain (only where useful)

## Database
- PostgreSQL

## Cache / Queue
- Redis
- BullMQ

## AI Providers
- OpenAI
- Anthropic Claude
- Google Gemini

---

# VSCode Project Structure

```txt
brainstorm-ai/
├── apps/
│   ├── api/
│   └── web/
│
├── packages/
│   ├── agents/
│   ├── orchestrator/
│   ├── prompts/
│   ├── shared/
│   ├── evaluators/
│   └── memory/
│
├── docker/
├── docs/
└── scripts/
```

---

# Recommended Agent Structure

```txt
packages/agents/
    ├── ai-architect/
    ├── fullstack/
    ├── ml-scientist/
    ├── cloud-architect/
    ├── qa/
    ├── llm-expert/
    ├── dba/
    ├── security/
    └── moderator/
```

---

# LangGraph Flow

## Step 1
User submits a problem.

## Step 2
Orchestrator analyzes:
- topic
- complexity
- constraints
- required experts

## Step 3
Relevant agents run independently.

## Step 4
Critic agents review outputs.

## Step 5
Contradictions are detected.

## Step 6
Synthesizer creates final response.

---

# Recommended State Shape

```ts
type BrainstormState = {
  userGoal: string;
  constraints: string[];
  activeAgents: string[];
  discussions: string[];
  risks: string[];
  decisions: string[];
  unresolvedQuestions: string[];
  consensusScore: number;
};
```

---

# Initial MVP

Start with only:

- Moderator
- AI Architect
- Full Stack Engineer
- QA Engineer
- Synthesizer

Avoid adding all agents initially.

---

# Suggested Backend Milestones

## Phase 1
- Setup NestJS
- Setup LangGraph
- Create orchestrator
- Create 3 agents
- Create shared state

## Phase 2
- Add Redis memory
- Add conversation persistence
- Add evaluation pipeline

## Phase 3
- Add streaming responses
- Add WebSockets
- Add execution visualization

## Phase 4
- Add security agent
- Add contradiction analysis
- Add scoring engine

## Phase 5
- Add human approval workflow
- Add execution replay
- Add analytics dashboard

---

# Recommended Prompt Strategy

Avoid giant prompts.

Instead:
- shared base system prompt
- small persona prompt
- strict output schema

---

# Important Engineering Rules

## 1. Keep Agents Stateless
Do not let every agent maintain permanent memory.

## 2. Limit Context
Only pass relevant context.

## 3. Avoid Infinite Loops
Set:
- max iterations
- timeout
- token budget

## 4. Store Everything
Persist:
- discussions
- outputs
- costs
- failures
- evaluations

## 5. Evaluate Continuously
Track:
- hallucination rate
- contradiction rate
- solution usefulness
- token cost
- execution time

---

# Recommended First Deliverable

Before building the UI:

Build a CLI prototype.

Reason:
- faster iteration
- easier debugging
- cheaper experimentation

Only build the frontend after orchestration quality is stable.

---

# Recommended Next Step

Build this first:

```txt
User Problem
    ↓
Moderator
    ↓
3 Expert Agents
    ↓
Critic
    ↓
Synthesizer
```

That alone is enough to validate the concept.
