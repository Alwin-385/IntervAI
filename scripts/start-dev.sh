#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Starting Postgres, Redis, and Qdrant..."
docker compose up -d postgres redis qdrant

echo ""
echo "Next steps:"
echo "  Backend:  cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm install && npm run dev"
