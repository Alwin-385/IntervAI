# AI Interview Intelligence Platform

Production-grade monorepo for AI-powered interview preparation and evaluation.

## Stack

| Layer | Technologies |
|-------|----------------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind, shadcn/ui, Zustand, TanStack Query, Framer Motion, Recharts |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic, PostgreSQL, Celery, Redis, LangGraph, Qdrant |
| Infra | Docker Compose |

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

## Local development (hybrid)

Start infrastructure only:

```powershell
.\scripts\start-dev.ps1
```

**Backend:**

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intervai
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Project structure

```
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── docker/            # Dockerfiles
├── docs/              # Documentation
├── scripts/           # Dev scripts
└── docker-compose.yml
```

## Linting

```bash
# Frontend
cd frontend && npm run lint && npm run format:check

# Backend
cd backend && ruff check app && ruff format --check app
```

## Phase 1 status

- [x] Monorepo scaffold
- [x] Health check API (`GET /api/v1/health`)
- [x] Landing page with backend connectivity
- [x] Docker Compose (Postgres, Redis, Qdrant, API, Celery, Frontend)
