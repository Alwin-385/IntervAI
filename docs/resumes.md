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

## Migration

```bash
cd backend
alembic upgrade head
```
