# AI Interview Intelligence Platform

Production-grade monorepo for AI-powered interview preparation and evaluation.

[![CI](https://github.com/yourname/intervai/actions/workflows/ci.yml/badge.svg)](https://github.com/yourname/intervai/actions/workflows/ci.yml)

## Stack

| Layer | Technologies |
|-------|----------------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind, shadcn/ui, Zustand, TanStack Query, Framer Motion, Recharts |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic, PostgreSQL, Celery, Redis, LangGraph, Qdrant |
| Auth | Clerk (JWT, JWKS verification) |
| Infra | Docker Compose (dev), Railway + Vercel (prod) |
| Security | Rate limiting, secure headers, prompt injection guards, PDF magic-byte validation |
| Monitoring | Sentry, structured JSON logs |

## Quick start (Docker)

1. Copy environment files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

2. Start all services:

```bash
docker compose up --build
```

3. Open:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

## Testing by phase

See **[docs/TESTING.md](docs/TESTING.md)** for how to run the stack and what to verify after each phase (health, auth, logout, resume upload, etc.).

## Local development (hybrid)

Start infrastructure only:

```powershell
.\scripts\start-dev.ps1
```

**Windows (from project root `c:\IntervAI`, two terminals after infra):**

```powershell
cd c:\IntervAI
.\scripts\start-backend.ps1   # path: c:\IntervAI — API on :8000
.\scripts\start-celery.ps1    # resume extraction worker (Redis required)
.\scripts\start-frontend.ps1  # path: c:\IntervAI — Next.js on :3000
```

See **[docs/TESTING.md](docs/TESTING.md)** for which folder each command uses.

**Backend (manual):** use the venv Python so `uvicorn` is found:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

**Frontend (manual):**

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Step-by-step checklists per phase: **[docs/TESTING.md](docs/TESTING.md)**.

## Project structure

```
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── docker/            # Dockerfiles
├── docs/              # Documentation
├── scripts/           # Dev scripts
└── docker-compose.yml
```

## Testing

```powershell
# Backend unit tests
cd backend
.\.venv\Scripts\pytest -m unit -q

# Frontend unit tests
cd frontend
npm test
```

## Linting

```bash
# Frontend
cd frontend && npm run lint && npm run format:check

# Backend
cd backend && ruff check app && ruff format --check app
```

## Deployment

See **[docs/DEPLOY.md](docs/DEPLOY.md)** for full deployment instructions:
- Vercel (frontend) + Railway (backend) — recommended
- Render blueprint
- Single-server VPS with Docker Compose
- CI/CD via GitHub Actions (automatic on push to `main`)

## Phase 19 — Security, Testing & Deployment

- [x] Rate limiting (IP-based, per-endpoint: 120/30/10 rpm)
- [x] Secure response headers (`X-Frame-Options`, `X-Content-Type-Options`, `HSTS`, etc.)
- [x] Prompt injection detection + sanitisation on all user-supplied text
- [x] AI output sanitiser (strips leaked prompt markers from LLM responses)
- [x] PDF magic-byte validation + MIME/extension allow-list
- [x] Sentry integration (errors + traces)
- [x] Backend pytest suite (security, auth, API, file validation, background jobs, config)
- [x] Frontend Jest suite (api-client, resume utils, analytics types, cn utility)
- [x] Production Dockerfiles (multi-stage, non-root user, healthchecks)
- [x] `docker-compose.prod.yml` (all services, named volumes, internal/external networks)
- [x] Railway config (`railway.toml`), Render blueprint (`render.yaml`)
- [x] Vercel config (`vercel.json` with security headers)
- [x] GitHub Actions CI (lint, test, Docker build check)
- [x] GitHub Actions CD (build + push GHCR, deploy Railway + Vercel)
- [x] Production env templates (`backend/.env.production.example`, `frontend/.env.production.example`)
- [x] Deployment guide (`docs/DEPLOY.md`)

## Phase 1 status

- [x] Monorepo scaffold
- [x] Health check API (`GET /api/v1/health`)
- [x] Landing page with backend connectivity
- [x] Docker Compose (Postgres, Redis, Qdrant, API, Celery, Frontend)

## Phase 3 — Authentication

- [x] Clerk on frontend (sign-in, sign-up, protected dashboard)
- [x] Clerk JWT verification on backend
- [x] `GET /api/v1/me` and `GET /api/me`
- [x] User sync to PostgreSQL

See [docs/auth.md](docs/auth.md) for Clerk setup.

## Phase 7 — AI Resume Analyzer

- [x] LangGraph pipeline (embeddings + structured analysis)
- [x] OpenAI provider + heuristic fallback
- [x] Qdrant chunk indexing
- [x] `POST/GET` resume analysis APIs
- [x] Analysis UI with scores, charts, recruiter feedback

See [docs/resume-analysis.md](docs/resume-analysis.md).

## Phase 4 — UI foundation

- [x] Full marketing landing page (hero, features, workflow, demo, CTA, footer)
- [x] Dashboard shell with sidebar + top navbar (mobile responsive)
- [x] Premium dashboard home (stats, quick actions, placeholders)
- [x] Framer Motion animations, skeletons, animated counters

## Phase 5 — Resume upload

- [x] Secure PDF upload (validation, size limits, local/S3 storage)
- [x] Drag-and-drop UI with progress bar
- [x] Replace resume flow

See [docs/resumes.md](docs/resumes.md).

## Phase 6 — Resume text extraction

- [x] Async PDF extraction (PyMuPDF → pdfplumber → pypdf fallback)
- [x] Text cleaning, section parsing, chunking
- [x] Structured fields (name, education, experience, skills, etc.)
- [x] Celery worker + Redis queue (`resume.extract`)
- [x] Status lifecycle: `queued` → `extracting_resume` → `completed` | `failed`
- [x] Extraction status API + frontend polling

**Upload fails with email error?** Add `CLERK_SECRET_KEY` to `backend/.env` (same Clerk app as the frontend). See [docs/TESTING.md](docs/TESTING.md).
