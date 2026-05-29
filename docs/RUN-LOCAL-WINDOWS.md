# Run IntervAI locally (Windows) — step by step

Use **3 terminals** plus Docker Desktop. Every command starts from:

```powershell
cd c:\IntervAI
```

Check what is running anytime:

```powershell
.\scripts\dev-status.ps1
```

---

## Step 0 — One-time setup

1. Install **Docker Desktop**, **Node.js 20+**, **Python 3.12+**.
2. Start **Docker Desktop** and wait until it says **Running**.
3. Create env files (if you have not already):

```powershell
cd c:\IntervAI
Copy-Item backend\.env.example backend\.env -ErrorAction SilentlyContinue
Copy-Item frontend\.env.example frontend\.env.local -ErrorAction SilentlyContinue
```

4. Edit `backend\.env`:
   - `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intervai`
   - `CELERY_BROKER_URL=redis://localhost:6379/1`
   - `RESUME_EXTRACTION_MODE=background`
   - `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001`
   - Clerk keys filled in

5. Edit `frontend\.env.local`:
   - `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - Clerk publishable key

6. Backend Python venv:

```powershell
cd c:\IntervAI\backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
cd c:\IntervAI
```

7. Frontend packages:

```powershell
cd c:\IntervAI\frontend
npm install
cd c:\IntervAI
```

---

## Step 1 — Terminal A: Database (Docker)

```powershell
cd c:\IntervAI
docker compose up -d postgres redis
```

Wait until you see containers **Started**.  
You do **not** need the Celery terminal for resume extraction (`RESUME_EXTRACTION_MODE=background`).

---

## Step 2 — Terminal B: Backend API

```powershell
cd c:\IntervAI
.\scripts\start-backend.ps1
```

Leave this window **open**. You should see:

- `Running database migrations...` (no error)
- `Uvicorn running on http://127.0.0.1:8000`

**Test in browser:** http://localhost:8000/api/v1/health  
You should see JSON (status ok / healthy).

If migration fails → Postgres is not running → repeat Step 1.

If port 8000 in use → stop the other backend (Ctrl+C in that terminal) or:

```powershell
netstat -ano | findstr :8000
taskkill /PID <pid> /F
.\scripts\start-backend.ps1
```

---

## Step 3 — Terminal C: Frontend

```powershell
cd c:\IntervAI
.\scripts\start-frontend.ps1
```

Leave this window **open**. You should see:

```text
Local:  http://localhost:3000
```

### Open the app

| URL | Use when |
|-----|----------|
| **http://localhost:3000** | Normal — use this |
| http://localhost:3001 | Only if the terminal says Next.js chose port **3001** |

**Internal Server Error on /** — restart frontend with `.\scripts\start-frontend.ps1 -KillStalePort` and use **http://localhost:3000** (not 127.0.0.1 in the browser if you had hostname issues).

**If http://localhost:3001 says “refused to connect”**  
Nothing is listening on 3001. Your app is almost certainly on **3000** — open that instead.

If port 3000 is busy:

```powershell
.\scripts\start-frontend.ps1 -KillStalePort
```

---

## Step 4 — Use the app

1. Open **http://localhost:3000**
2. Sign in (Clerk)
3. Go to **Dashboard → Resumes**
4. Upload a PDF — status should move from **Starting…** → **Extracting…** → **Ready** within ~30 seconds

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `localhost:3001` refused | Use **http://localhost:3000** or run `.\scripts\dev-status.ps1` |
| Cannot reach API at :8000 | Start backend (Step 2); open http://localhost:8000/api/v1/health |
| API error on 3001 but OK on 3000 | Add 3001 to `CORS_ORIGINS` in `backend\.env` and **restart backend** |
| Resume stuck on Queued | Click **Run extraction** on the card; ensure `RESUME_EXTRACTION_MODE=background` |
| Script not found | Run from `c:\IntervAI`, not `c:\IntervAI\backend` |
| Docker pipe error | Start Docker Desktop first |

---

## What you do NOT need for local dev

- `.\scripts\start-celery.ps1` (optional; background extraction runs in the API)
- Port 3001 (unless Next.js explicitly prints that port)

---

## Quick copy-paste (daily)

```powershell
# Terminal A
cd c:\IntervAI
docker compose up -d postgres redis

# Terminal B
cd c:\IntervAI
.\scripts\start-backend.ps1

# Terminal C
cd c:\IntervAI
.\scripts\start-frontend.ps1
```

Then open: **http://localhost:3000**
