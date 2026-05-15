# Continuity Engine

A persistent memory system for AI models. Every conversation message is tagged with importance (1–10), detected emotion, topics, and a timestamp. A smart retrieval layer surfaces the most relevant past messages — not just recent ones — so the AI responds as if it genuinely knows you over time.

## Run & Operate

- **Continuity Engine** — start the "Continuity Engine" workflow in the Shell tab to chat interactively
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)
- **Continuity Engine**: Python 3, `requests`, OpenRouter (Mistral via Replit AI Integrations)

## Where things live

- `continuity_engine/` — all Python source files for the memory system
  - `main.py` — CLI loop (entry point)
  - `memory.py` — JSON persistence (`memory.json`)
  - `ai.py` — OpenRouter API call (Mistral)
  - `emotions.py` — keyword-based emotion detection
  - `importance.py` — message importance scoring (1–10)
  - `patterns.py` — recurring topic and emotion pattern analysis
  - `retrieval.py` — smart context retrieval with multi-factor scoring
  - `summaries.py` — live summary generation
  - `topics.py` — topic tagging (AI, coding, project, future, etc.)
  - `memory.json` — persistent conversation store

## Architecture decisions

- **File-based memory** — `memory.json` stores all messages with metadata. Simple and portable; easy to inspect and edit manually.
- **Scored retrieval** — context selection uses a weighted scoring model (topic overlap 0–25 pts, importance ×3, recency 0–15, exact match +40, recency boost +10) instead of naive last-N messages.
- **Intent routing** — `detect_intent()` distinguishes IDENTITY queries (personal/emotional) from SESSION queries (factual), applying a hard filter on the latter to avoid noisy context.
- **No embeddings** — everything is keyword-based. Zero external dependencies beyond `requests`. Fast and interpretable.
- **Replit AI Integrations for OpenRouter** — `AI_INTEGRATIONS_OPENROUTER_BASE_URL` and `AI_INTEGRATIONS_OPENROUTER_API_KEY` are auto-provisioned; no user API key required.

## Product

A CLI chatbot backed by a multi-dimensional memory system. The AI (Mistral via OpenRouter) receives a continuity summary of recurring topics and emotional patterns alongside the most relevant retrieved messages, producing responses that feel contextually aware over long time horizons.

## User preferences

- Project name: Sarvix (referenced in topics.py and memory.json — appears to be the user's startup/build project)

## Gotchas

- The workflow is set to `autoStart: false` — start it manually from the Shell tab
- `memory.json` path is resolved relative to `memory.py` so the file always lands in `continuity_engine/` regardless of working directory
- Run from within `continuity_engine/` or via the workflow command which `cd`s there first

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
