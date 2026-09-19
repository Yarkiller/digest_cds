# Local platform runbook (Phase 1)

Step-by-step bring-up for **local Vite + local FastAPI** against the **existing remote** self-hosted Supabase VM (`knowledge-db.ru`). This is the Phase 1 success path (D-05 / PLAT-08).

**Not required for success:** a second local Docker Supabase (PLAT-01). Schema/RLS from [`supabase-integration/migrations/001_initial_schema.sql`](../../supabase-integration/migrations/001_initial_schema.sql) is already applied on the VM — do **not** re-provision or run destructive resets against the shared instance.

**Live E2E gating (RESOLVED RESEARCH Q3):** the checklist below (or optional local Playwright with live env) proves FE↔BE. Phase 1 is **not** blocked on CI live credentials.

---

## 1. Environment

1. Copy [`.env.example`](../../.env.example) → `.env` at the repo root (gitignored).
2. Fill **backend / Supabase** values (never commit real keys):
   - `SUPABASE_URL` — e.g. `https://knowledge-db.ru`
   - `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY`
   - `SUPABASE_JWKS_URL` / `SUPABASE_JWT_ISSUER` (must match Auth JWT issuer used by the VM)
   - `API_CORS_ORIGINS` — include Vite origins, e.g.  
     `http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:5174,http://localhost:5174`
   - `ALLOWED_EMAIL_DOMAINS=@sberbank.ru,@omega.sbrf.ru`
   - `APP_CONTAINER=live` for ping persistence (default `memory` keeps unit tests offline)
3. Fill **Vite publishable-only** vars (never put `SUPABASE_SECRET_KEY` behind a `VITE_` prefix):
   - `VITE_SUPABASE_URL` / `VITE_SUPABASE_PUBLISHABLE_KEY`
   - `VITE_API_BASE_URL=http://127.0.0.1:8000`
   - `VITE_USE_MOCKS=true` for Playwright / offline UI (default)
   - `VITE_USE_MOCKS=false` **only** for the live FE↔BE proof (D-09 / D-10)

Threat note (T-01-13): keep secrets in `.env` only — do not paste keys into markdown, commits, or screenshots.

---

## 2. Backend (FastAPI)

```bash
# from repo root
uv sync
# live adapters → profiles + activity_events (service_role only in composition/live.py)
# --env-file .env is REQUIRED: settings read os.environ and nothing auto-loads .env.
# Without it APP_CONTAINER defaults to `memory` and JWKS/CORS are empty (ping won't persist).
uv run --env-file .env uvicorn backend.interface.http.app:create_default_app --factory --host 127.0.0.1 --port 8000
```

Smoke: `GET http://127.0.0.1:8000/health` should return OK. Structured JSON logs on stdout include `request_id` on each request (PLAT-06).

Optional helper (prints this path + the uvicorn command, no secrets):

```bash
npm run platform:runbook
```

---

## 3. Frontend (Vite)

```bash
npm install
npm install --prefix web
npm run dev
```

Vite loads env from the **`web/`** dir (its config root), **not** the repo-root `.env`. For the live proof create **`web/.env.local`** (gitignored) with the publishable-only vars:

```dotenv
VITE_SUPABASE_URL=https://knowledge-db.ru
VITE_SUPABASE_PUBLISHABLE_KEY=<publishable key>
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_USE_MOCKS=false
```

Restart `npm run dev` after creating/editing it — Vite only reads env files at startup. With `VITE_USE_MOCKS` unset or `true`, `RequireAuth` renders through and `/login` is never shown (mock data). Open [http://127.0.0.1:5173](http://127.0.0.1:5173). Playwright web project uses port **5174** under mocks — keep CORS allowlist covering both.

---

## 4. Auth users (amended D-08 / G-01-3)

**Primary path — self-service registration:** new operators use SPA `/register` with corporate email, password, and display nickname **«Логин»** (publishable-client `signUp` only — never `service_role` in the browser).

**Ops fallback — shared VM dashboard seed:** if you need a pre-created test account without going through `/register`:

1. Open the Supabase Auth dashboard for the knowledge-db.ru project.
2. Create **1–2** users with corporate emails only (`@sberbank.ru` or `@omega.sbrf.ru`).
3. Set passwords you control locally; do not commit credentials.
4. Optional: if this self-host Auth build exposes a domain allowlist/hook, enable the two corporate domains. Otherwise defense-in-depth is UI + FastAPI claim checks (D-04 / AUTH-01).

Shared VM: **no automated seed script** against `knowledge-db.ru`. First successful `GET /me` upserts `profiles` via `ProfileRepository.get_or_upsert` (idempotent safety net if no Auth→profiles trigger is present).

Do **not** run DROP/TRUNCATE/reset SQL on the shared VM during proof (T-01-14). Ping is insert-only (`activity_events`, `kind=platform_ping`).

---

## 5. Live FE↔BE proof checklist (D-10)

With API on `:8000`, Vite on `:5173`, `APP_CONTAINER=live`, and `VITE_USE_MOCKS=false`:

1. **Existing user:** open `/login` and sign in with corporate **email + password only** (no name/«Логин» field on login) → land on current issue `/` (or honor `returnUrl`). Header shows the stored display name (or email fallback), not the mock «Мария Сидорова».
2. **New user:** open `/register`, fill email, password, and **«Логин»** (display nickname) → after successful signUp, land on issue (or `returnUrl`). «Логин» is saved to `profiles.display_name` / Auth metadata at registration only.
3. Confirm **GET /me** succeeds — PlatformProofBanner shows name/email/role, or Network tab shows HTTP 200 with `display_name`.
4. Click **«Проверить ping»** (POST `/me/ping`) → banner shows `ok · id …`.
5. Confirm a new `activity_events` row with `kind = platform_ping` (Studio SQL / MCP `query` — **select/insert only**, no destructive DDL).
6. Attempt a **disallowed** domain on `/login` or `/register` — inline rejection; no usable session (AUTH-01).
7. In API stdout, confirm structured logs include `request_id` for the `/me` and `/me/ping` calls.

Phase 1 platform proof is this checklist. Issue/vote content may still be mock until later phases (D-12).
