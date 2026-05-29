# Authentication (Clerk)

## Setup

1. Create an application at [Clerk Dashboard](https://dashboard.clerk.com).
2. Copy API keys into environment files.

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### Backend (`backend/.env`)

```env
CLERK_SECRET_KEY=sk_test_...
CLERK_JWT_ISSUER=https://your-instance.clerk.accounts.dev
```

Find **JWT issuer** in Clerk → **Configure** → **API Keys** → **Advanced**.

## User flow

1. Landing page → Sign up / Log in (Clerk UI)
2. Redirect to `/dashboard` after authentication
3. Frontend sends `Authorization: Bearer <session_token>` to the API
4. Backend verifies JWT via JWKS
5. If the token has no `email` claim (common for default Clerk session tokens), the backend loads the profile from the **Clerk Backend API** using `CLERK_SECRET_KEY`
6. User is synced to PostgreSQL; `GET /api/v1/me` or `GET /api/me` returns the profile

Without `CLERK_SECRET_KEY` on the backend, upload and `/me` may fail with an email-related error.

## Protected routes

| Layer | Protection |
|-------|------------|
| Frontend | `middleware.ts` — `/dashboard/*` requires Clerk session |
| Backend | `Depends(get_current_user)` on resource endpoints |
