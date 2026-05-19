# Architecture Overview

## Monorepo layout

| Path | Purpose |
|------|---------|
| `frontend/` | Next.js 15 SPA — interview UI, dashboards, analytics |
| `backend/` | FastAPI API — auth, sessions, AI orchestration, scoring |
| `docker/` | Container definitions |
| `docs/` | Technical documentation |
| `scripts/` | Development and deployment helpers |

## API versioning

All REST endpoints are namespaced under `/api/v1/`. Future versions will use `/api/v2/` without breaking existing clients.

## Async-first backend

- **SQLAlchemy 2.0** async sessions via `asyncpg`
- **Celery** workers for long-running AI and speech jobs
- **Redis** for caching and Celery broker
- **Qdrant** for vector retrieval (RAG, question banks)
- **LangGraph** for multi-step interview agent workflows

## Frontend data layer

- **TanStack Query** — server state, caching, retries
- **Zustand** — lightweight client UI state
- **shadcn/ui** — accessible, themeable components
