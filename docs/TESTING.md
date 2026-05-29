# IntervAI — Run & test guide (Phases 1–6)

Step-by-step instructions for **Windows PowerShell**. Use **four terminals** (database, backend, Celery, frontend) for Phase 6 extraction.

## Where to run each command

| What you do | Folder path (run `cd` here first) | File / script used |
|-------------|-----------------------------------|---------------------|
| Start Postgres | `c:\IntervAI` | `docker-compose.yml` |
| Start backend (script) | `c:\IntervAI` | `scripts\start-backend.ps1` |
| Start frontend (script) | `c:\IntervAI` | `scripts\start-frontend.ps1` |
| Infra helper | `c:\IntervAI` | `scripts\start-dev.ps1` |
| Backend env | `c:\IntervAI\backend` | `.env` (copy from `.env.example`) |
| Frontend env | `c:\IntervAI\frontend` | `.env.local` (copy from `.env.example`) |
| Migrations (manual) | `c:\IntervAI\backend` | `.venv\Scripts\alembic.exe` |
| API server (manual) | `c:\IntervAI\backend` | `.venv\Scripts\python.exe` → `app\main.py` |
| Frontend dev server (manual) | `c:\IntervAI\frontend` | `package.json` → `npm run dev` |

Project root = `c:\IntervAI` (folder that contains `frontend\`, `backend\`, `scripts\`, `docker-compose.yml`).

---

## First-time setup (once per machine)

### 1. Install tools

| Tool | Check |
|------|--------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | `docker --version` |
| [Node.js 20+](https://nodejs.org/) | `node --version` |
| [Python 3.12+](https://www.python.org/) | `python --version` |

### 2. Open project root

**Path:** `c:\IntervAI`

```powershell
cd c:\IntervAI
```

Your prompt should end with `...\IntervAI>`.

### 3. Create environment files

**Path:** `c:\IntervAI` (commands create files in `backend\` and `frontend\`)

```powershell
cd c:\IntervAI
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env.local
```

Edit file **`c:\IntervAI\backend\.env`**:

- `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intervai`
- `CLERK_SECRET_KEY=sk_test_...` (from [Clerk Dashboard](https://dashboard.clerk.com))
- `CLERK_JWT_ISSUER=https://YOUR-INSTANCE.clerk.accounts.dev`

Edit file **`c:\IntervAI\frontend\.env.local`**:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...`
- `CLERK_SECRET_KEY=sk_test_...` (same Clerk app)

### 4. Backend Python virtual environment

```powershell
cd c:\IntervAI\backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 5. Frontend dependencies

```powershell
cd c:\IntervAI\frontend
npm install
```

---

## Every time you work on the project

You need **3 things running**: Postgres (Docker), backend API, frontend app.

### Terminal A — Database (Docker)

| Item | Value |
|------|--------|
| **Path** | `c:\IntervAI` |
| **Config file** | `docker-compose.yml` |

```powershell
cd c:\IntervAI
docker compose up -d postgres
```

Wait until Postgres is up (`docker compose ps` shows `postgres` running).

### Terminal B — Backend API

| Item | Value |
|------|--------|
| **Path (script)** | `c:\IntervAI` → run `.\scripts\start-backend.ps1` |
| **Path (manual)** | `c:\IntervAI\backend` |
| **Env file** | `c:\IntervAI\backend\.env` |

**Option A — helper script (recommended):**

```powershell
cd c:\IntervAI
.\scripts\start-backend.ps1
```

**Option B — manual commands (run from backend folder):**

```powershell
cd c:\IntervAI\backend
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see: `Uvicorn running on http://127.0.0.1:8000`

**Do not** run bare `uvicorn ...` unless you activated the venv first. On Windows, `uvicorn` is only on PATH **inside** the venv:

```powershell
cd c:\IntervAI\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

If activation is blocked by policy, use Option A or `python -m uvicorn` as above.

### Terminal C — Frontend

| Item | Value |
|------|--------|
| **Path (script)** | `c:\IntervAI` → run `.\scripts\start-frontend.ps1` |
| **Path (manual)** | `c:\IntervAI\frontend` |
| **Env file** | `c:\IntervAI\frontend\.env.local` |

**Option A — helper script:**

```powershell
cd c:\IntervAI
.\scripts\start-frontend.ps1
```

**Option B — manual (run from frontend folder):**

```powershell
cd c:\IntervAI\frontend
npm run dev
```

You should see: `Local: http://localhost:3000`

### Verify URLs

| URL | Expected |
|-----|----------|
| http://localhost:8000/api/v1/health | JSON with healthy status |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:3000 | Landing page |

---

## Common errors

| Error | Cause | Fix |
|-------|--------|-----|
| `uvicorn is not recognized` | Wrong folder or venv not used | `cd c:\IntervAI\backend` then `.\.venv\Scripts\python -m uvicorn ...` or run script from `c:\IntervAI` |
| Parse error in `start-backend.ps1` | Old script with `+` in strings | Pull latest script; use single-quote messages (fixed) |
| `Connection refused` on `alembic` | Postgres container stopped | `docker compose up -d postgres` |
| Upload / email errors | Missing backend Clerk secret | Set `CLERK_SECRET_KEY` in `backend\.env`, restart backend |
| `Failed to fetch` / network error on upload | Backend not running or wrong port | **Path `c:\IntervAI`:** `.\scripts\start-backend.ps1` — open http://localhost:8000/api/v1/health |
| Port 8000 already in use | Old uvicorn still running | Stop other backend terminal, or `.\scripts\start-backend.ps1 -Port 8001` and update `frontend\.env.local` |
| Dashboard works but upload fails | API crashed on user create (enum bug) | Restart backend after pulling latest code |
| `Activate.ps1` cannot be loaded | PowerShell execution policy | Use `python -m uvicorn` path above, or run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## Phase 1 — Monorepo & health

**Built:** Repo layout, Docker Compose, health API, basic landing.

### How to run

Follow **Every time** steps (Terminals A, B, C).

### What to check

- [ ] http://localhost:8000/api/v1/health returns success JSON
- [ ] http://localhost:3000 loads without a blank page
- [ ] Backend terminal shows no traceback on startup

---

## Phase 2 — Database & CRUD APIs

**Built:** Models, Alembic migrations, repository layer, CRUD APIs.

### How to run

Same as Phase 1. Migrations run automatically in `start-backend.ps1`, or run manually:

```powershell
cd c:\IntervAI\backend
.\.venv\Scripts\alembic upgrade head
```

### What to check

- [ ] `alembic upgrade head` prints no errors
- [ ] http://localhost:8000/docs lists `/api/v1/users`, resumes, sessions, etc.
- [ ] Postgres has tables (`users`, `resumes`, …) — optional: `docker exec -it intervai-postgres-1 psql -U postgres -d intervai -c "\dt"`

---

## Phase 3 — Clerk authentication

**Built:** Sign-in/up, protected dashboard, JWT verification, `GET /api/v1/me`, user sync.

### How to run

Same stack + Clerk keys in both env files.

### What to check

- [ ] http://localhost:3000/sign-in — sign up or log in
- [ ] Redirect to http://localhost:3000/dashboard
- [ ] Top bar shows your email (from `/api/v1/me`)
- [ ] **Log out:** click **Log out** (header or sidebar) or avatar → Sign out → home page `/`
- [ ] Sign in again — still works

---

## Phase 4 — Landing & dashboard UI

**Built:** Full marketing landing, dashboard shell, sidebar, mobile menu.

### How to run

Same stack; must be signed in for dashboard.

### What to check

- [ ] Landing: hero, features, workflow, demo section, footer
- [ ] `/dashboard` — sidebar links (Overview, Interviews, Resumes, …)
- [ ] Resize to mobile — menu opens sidebar
- [ ] Logged-out user visiting `/dashboard` is sent to sign-in

---

## Phase 5 — Resume upload

**Built:** PDF upload API, drag-and-drop UI, list/delete/replace.

### How to run

Same stack; **`CLERK_SECRET_KEY` must be in `backend\.env`** (for email lookup on upload).

### What to check

- [ ] http://localhost:3000/dashboard/resumes
- [ ] Upload a PDF under 5 MB — progress bar, success message
- [ ] File appears in the list
- [ ] Delete removes it
- [ ] Upload non-PDF — clear error, no crash
- [ ] Log out and log back in — resumes still listed (same account)

Files are stored under `backend\storage\resumes\` by default.

---

## Full smoke test (all phases)

1. `docker compose up -d postgres`
2. Terminal B: `.\scripts\start-backend.ps1`
3. Terminal C: `.\scripts\start-frontend.ps1`
4. Open http://localhost:3000 → sign in → Dashboard → Resumes → upload PDF
5. Log out → sign in → resume still there
6. http://localhost:8000/api/v1/health still OK

---

## Quick reference (copy-paste)

```powershell
# ----- Terminal A (path: c:\IntervAI) -----
cd c:\IntervAI
docker compose up -d postgres

# ----- Terminal B (path: c:\IntervAI, script: scripts\start-backend.ps1) -----
cd c:\IntervAI
.\scripts\start-backend.ps1

# ----- Terminal C (path: c:\IntervAI, script: scripts\start-frontend.ps1) -----
cd c:\IntervAI
.\scripts\start-frontend.ps1
```

**Manual backend instead of script (path: c:\IntervAI\backend):**

```powershell
cd c:\IntervAI\backend
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Manual frontend (path: c:\IntervAI\frontend):**

```powershell
cd c:\IntervAI\frontend
npm run dev
```

---

## Phase 6 — Resume text extraction

### Run

1. `docker compose up -d postgres redis` (from `c:\IntervAI`)
2. `.\scripts\start-backend.ps1`
3. `.\scripts\start-celery.ps1` (or rely on inline fallback if Redis is down)
4. `.\scripts\start-frontend.ps1`
5. `cd backend; .\.venv\Scripts\alembic upgrade head` (adds extraction columns + new status enum)

### Verify

| Step | Expected |
|------|----------|
| Upload PDF | Response `status: "queued"`; card shows **Queued** then **Extracting** |
| Wait ~5–30s | Status **Ready** (`completed`); skills badges appear |
| `GET /api/v1/resumes/{id}/extraction` | `extracted_data` with sections; `chunk_count` > 0 |
| Broken/scanned PDF | `status: "failed"` + `extraction_error`; **Retry extraction** works |

Without Celery: upload still works — broker failure runs extraction inline in the API process.

---

## Next phases

When new features ship, this doc will add a section with run steps and a checklist for that phase.
