# IntervAI — Deployment Guide

## Architecture overview

| Layer | Local dev | Production |
|-------|-----------|------------|
| **Frontend** | Next.js (`npm run dev`) | Vercel |
| **Backend API** | Uvicorn (`start-backend.ps1`) | Railway or Render |
| **Celery worker** | Optional (`start-celery.ps1`) | Railway worker service |
| **PostgreSQL** | Docker (`docker compose up postgres`) | Neon (serverless Postgres) |
| **Redis** | Docker (`docker compose up redis`) | Upstash (serverless Redis) |
| **Vector store** | Optional Docker Qdrant | Qdrant Cloud |
| **File storage** | Local `./storage/` | AWS S3 or Cloudflare R2 |
| **Auth** | Clerk (dev keys) | Clerk (production keys) |
| **Monitoring** | Structured logs | Sentry + structured JSON logs |

---

## Option A — Vercel (frontend) + Railway (backend) ← recommended

### 1. Prepare the repository

```bash
git remote add origin https://github.com/yourname/intervai.git
git push -u origin main
```

### 2. Provision managed services

#### Neon PostgreSQL
1. Sign up at https://neon.tech (free tier available)
2. Create project → **Copy connection string**
3. Replace `postgresql://` with `postgresql+asyncpg://` and add `?sslmode=require`

#### Upstash Redis
1. Sign up at https://upstash.com (free tier available)
2. Create database → **Copy** the `rediss://` connection string
3. Use same URL for `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` (append `/1`, `/2` for broker/backend)

#### Qdrant Cloud (optional — skip if using heuristic-only mode)
1. Sign up at https://cloud.qdrant.io
2. Create cluster → **Copy** URL and API key

### 3. Deploy backend to Railway

1. Go to https://railway.app → New Project → **Deploy from GitHub**
2. Select your repo; Railway will detect `railway.toml`
3. Go to **Variables** tab and paste all values from `backend/.env.production.example`
4. Railway assigns a domain like `intervai-backend.up.railway.app` — note it

**Required Railway environment variables:**

```
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://...@neon.tech/intervai?sslmode=require
REDIS_URL=rediss://default:xxx@upstash.io:6379
CELERY_BROKER_URL=rediss://default:xxx@upstash.io:6379/1
CELERY_RESULT_BACKEND=rediss://default:xxx@upstash.io:6379/2
CLERK_SECRET_KEY=sk_live_xxx
CLERK_JWT_ISSUER=https://your-app.clerk.accounts.dev
OPENAI_API_KEY=sk-proj-xxx
CORS_ORIGINS=https://your-app.vercel.app
STORAGE_BACKEND=s3
S3_BUCKET=intervai-resumes-prod
S3_ACCESS_KEY_ID=xxx
S3_SECRET_ACCESS_KEY=xxx
SENTRY_DSN=https://xxx@sentry.io/xxx
```

Run database migrations — Railway runs `alembic upgrade head` in the start command automatically.

### 4. Add Celery worker on Railway

1. In the same Railway project → **New Service** → **Empty Service**
2. Connect same repo; set **Start command**:
   ```
   celery -A app.workers.celery_app worker --loglevel=info -Q default,resume,interview,ai --concurrency=2
   ```
3. Set the same environment variables as the backend service

### 5. Deploy frontend to Vercel

1. Go to https://vercel.com → **Add New Project** → import from GitHub
2. Set **Root Directory** to `frontend`
3. Add environment variables:

```
NEXT_PUBLIC_API_URL=https://intervai-backend.up.railway.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxx
CLERK_SECRET_KEY=sk_live_xxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

4. Click **Deploy**

### 6. Update CORS on backend

Add your Vercel URL to `CORS_ORIGINS` in Railway, e.g.:
```
CORS_ORIGINS=https://intervai.vercel.app,https://www.intervai.app
```

---

## Option B — Render (backend) + Vercel (frontend)

1. Push your repo to GitHub
2. At https://render.com → **New** → **Blueprint** → select repo with `render.yaml`
3. Render will create backend, Celery worker, and a managed Postgres database
4. Fill in the environment variables marked `sync: false` in the Render dashboard
5. Deploy frontend to Vercel (same as step 5 above)

---

## Option C — Single-server VPS (Docker Compose)

For a single VPS (DigitalOcean Droplet, Hetzner, AWS EC2):

```bash
# On the server
git clone https://github.com/yourname/intervai.git
cd intervai
cp .env.prod.example .env
nano .env   # fill in your values

docker compose -f docker-compose.prod.yml up -d
```

Access at `http://your-server-ip:3000`.

Set up Nginx + Certbot for HTTPS:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## CI/CD Pipeline (GitHub Actions)

The `.github/workflows/ci.yml` runs on every push/PR:

| Job | What it does |
|-----|-------------|
| `backend-lint` | Ruff lint + format check |
| `backend-test` | pytest unit tests with Postgres + Redis |
| `frontend-lint` | ESLint + Prettier |
| `frontend-test` | TypeScript check + Jest |
| `docker-build` | Build Docker images (on main branch only) |

The `.github/workflows/deploy.yml` runs on push to `main`:

1. Builds and pushes Docker images to GHCR
2. Deploys backend to Railway via CLI
3. Deploys frontend to Vercel via CLI

**Required GitHub Secrets:**

| Secret | Description |
|--------|-------------|
| `RAILWAY_TOKEN` | From Railway → Account Settings → Tokens |
| `VERCEL_TOKEN` | From Vercel → Account → Tokens |
| `VERCEL_ORG_ID` | From `vercel whoami` |
| `VERCEL_PROJECT_ID` | From `.vercel/project.json` after `vercel link` |
| `BACKEND_URL` | Your Railway backend URL for health check |
| `NEXT_PUBLIC_API_URL` | Your Railway backend URL (used in frontend build) |

---

## Health checks

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/health` | Liveness — confirms API process is running |
| `GET /api/v1/ready` | Readiness — verifies database connectivity |

Configure these in Railway / Render as the health check path.

---

## Monitoring

### Sentry
1. Create a project at https://sentry.io
2. Copy DSN → set `SENTRY_DSN` in backend environment
3. Errors, exceptions, and slow transactions are automatically captured

### Logs
- **Local:** structured stdout via `structlog`
- **Production:** set `LOG_JSON=true` — logs emit newline-delimited JSON, compatible with Datadog, Logtail, and CloudWatch

---

## Security checklist

- [x] JWT verification via Clerk JWKS
- [x] Prompt injection patterns stripped from user input
- [x] AI output sanitised before returning to client
- [x] PDF magic-byte validation on every upload
- [x] File extension + MIME type allow-list enforced
- [x] Secure HTTP headers (`X-Frame-Options`, `X-Content-Type-Options`, `HSTS`, etc.)
- [x] IP-based rate limiting (120 rpm default, 30 rpm AI endpoints, 10 rpm uploads)
- [x] CORS allow-list — wildcard disabled in production
- [x] Environment isolation — `.env` never committed
- [x] Non-root Docker user in production images
- [x] `docs_url` and `redoc_url` hidden in production

---

## Rollback

**Railway:** Deployments → select previous deploy → **Redeploy**

**Vercel:** Deployments → three-dot menu → **Promote to production**

**Database:** Alembic downgrade:
```bash
alembic downgrade -1
```
