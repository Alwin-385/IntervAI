# Phase 7 — AI Resume Analyzer

## Backend

- **POST** `/api/v1/resumes/{id}/analyze` — start analysis (202)
- **GET** `/api/v1/resumes/{id}/analysis` — latest analysis result

Pipeline: LangGraph (`embed` → `analyze`), OpenAI embeddings → Qdrant `resume_chunks`, structured JSON in `resume_analyses.raw_analysis`.

### Env (`backend/.env`)

```env
OPENAI_API_KEY=sk-...          # optional; heuristic fallback if empty
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_URL=http://localhost:6333
```

Start Qdrant: `docker compose up -d postgres redis qdrant`

## Frontend

- **Analyze resume** on each Ready card → `/dashboard/resumes/{id}/analysis`
- Progress UI while `pending` / `processing`
- Scores, radar, ATS bars, recruiter feedback when `completed`

## Run (short)

```powershell
cd c:\IntervAI
docker compose up -d postgres redis qdrant
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

Open http://localhost:3000 → Resumes → **Analyze resume**.
