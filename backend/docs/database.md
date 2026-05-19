# Database Layer

## Models

| Table | Description |
|-------|-------------|
| `users` | Platform accounts |
| `resumes` | Uploaded resume documents |
| `resume_analyses` | AI analysis results for resumes |
| `interview_sessions` | Mock interview sessions |
| `interview_questions` | Questions per session |
| `interview_answers` | Candidate answers |
| `answer_evaluations` | Scored feedback per answer |
| `speech_analyses` | Speech metrics (answer or session level) |
| `weak_areas` | Identified skill gaps |
| `roadmaps` | Personalized learning plans |

## Migrations

```bash
cd backend
alembic upgrade head
```

Create a new revision after model changes:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Architecture

```
API → Service → Repository → SQLAlchemy → PostgreSQL
```

- **Repositories**: CRUD and queries only
- **Services**: validation, business rules, schema mapping
- **Dependencies**: FastAPI `Depends()` wiring per request
