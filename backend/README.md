# Backend — AI Interview Intelligence Platform

FastAPI backend with async SQLAlchemy, Celery, Redis, LangGraph, and Qdrant.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Linting

```bash
ruff check app
ruff format app
```

## Migrations

Ensure PostgreSQL is running and `DATABASE_URL` is set in `.env`.

```bash
alembic upgrade head
```

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

See [docs/database.md](../docs/database.md) for schema details.

## API (Phase 2)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/users` | Create user |
| GET | `/api/v1/users` | List users (paginated) |
| GET | `/api/v1/users/{id}` | Get user |
| PATCH | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |
| POST | `/api/v1/resumes` | Create resume |
| GET | `/api/v1/resumes/user/{user_id}` | List resumes |
| POST | `/api/v1/interview-sessions` | Create session |
| POST | `/api/v1/weak-areas` | Create weak area |
| POST | `/api/v1/roadmaps` | Create roadmap |
