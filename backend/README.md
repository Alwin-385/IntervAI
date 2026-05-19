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

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```
