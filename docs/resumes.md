# Resume Upload

## Endpoints

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/resumes/upload` | Bearer token |
| GET | `/api/v1/resumes` | Bearer token |
| GET | `/api/v1/resumes/{id}` | Bearer token |

Aliases (spec-compatible): `/api/resumes/upload`, `/api/resumes`, `/api/resumes/{id}`

## Upload (multipart)

- **Field `file`**: PDF only
- **Field `title`** (optional): display name
- **Field `replace_resume_id`** (optional): UUID of resume to replace

## Limits

- Max size: `RESUME_MAX_SIZE_BYTES` (default 5 MB)
- MIME: `application/pdf`
- Magic bytes: `%PDF`

## Storage

| Backend | Env |
|---------|-----|
| Local | `STORAGE_BACKEND=local`, `STORAGE_LOCAL_PATH=./storage/resumes` |
| S3-compatible | `STORAGE_BACKEND=s3`, `S3_BUCKET`, keys, optional `S3_ENDPOINT_URL` |

## Text extraction (Phase 6)

After upload, status flows: `queued` → `extracting_resume` → `completed` | `failed`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/resumes/{id}/extraction` | Poll extraction status and structured fields |
| POST | `/api/v1/resumes/{id}/extraction/retry` | Re-queue extraction |

Structured fields in `extracted_data`: name, education, projects, experience, skills, certifications, internships, achievements.

**Default:** extraction runs in the API process after upload (`RESUME_EXTRACTION_MODE=background`) — no Celery worker needed.

**Optional Celery** (`RESUME_EXTRACTION_MODE=celery` + Redis on `localhost`):

```powershell
.\scripts\start-celery.ps1
```

## Migration

```bash
cd backend
alembic upgrade head
```
