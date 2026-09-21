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

### 4.1 Auth mailer / autoconfirm (G-01-3b — required for `/register`)

On `knowledge-db.ru`, GoTrue had `mailer_autoconfirm=false` and a broken SMTP path. Signup then returned **500** `Error sending confirmation email` and **no Auth user was created**.

**Phase 1 unblock (do this now):** enable autoconfirm so signup does not depend on email:

1. Open Supabase Studio → **Authentication** → **Providers** → **Email**.
2. Turn **Confirm email** **OFF** (equivalent env: `GOTRUE_MAILER_AUTOCONFIRM=true` + restart Auth/GoTrue on the VM).
3. Verify: `GET https://knowledge-db.ru/auth/v1/settings` shows `"mailer_autoconfirm":true`.
4. Smoke: `POST /auth/v1/signup` with a new `@sberbank.ru` / `@omega.sbrf.ru` address returns **2xx** and the user appears under Authentication → Users.

**SMTP (ops ticket — not Phase 1):** keep a ticket to configure a working mailer. Until SMTP is healthy, **do not ship product features that depend on outbound email** (password-reset links, invite-by-email, confirmation flows). Self-service `/register` is allowed only because autoconfirm removes the email dependency. Revisit SMTP after Phase 1.

**SPA follow-up (deferred):** map mailer/confirmation failures to honest Russian copy — never the generic «Сервис входа временно недоступен» NETWORK banner (see `.planning/debug/g-01-3b-signup-mailer.md`).

**Ops fallback — shared VM dashboard seed:** if you need a pre-created test account without going through `/register`:

1. Open the Supabase Auth dashboard for the knowledge-db.ru project.
2. Create **1–2** users with corporate emails only (`@sberbank.ru` or `@omega.sbrf.ru`).
3. Set passwords you control locally; do not commit credentials.
4. Optional: if this self-host Auth build exposes a domain allowlist/hook, enable the two corporate domains. Otherwise defense-in-depth is UI + FastAPI claim checks (D-04 / AUTH-01).

Shared VM: **no automated seed script** against `knowledge-db.ru`. First successful `GET /me` upserts `profiles` via `ProfileRepository.get_or_upsert` (idempotent safety net if no Auth→profiles trigger is present).

Do **not** run DROP/TRUNCATE/reset SQL on the shared VM during proof (T-01-14). Ping is insert-only (`activity_events`, `kind=platform_ping`).

---

## 4b. Phase 2 content seed (D-25, D-27)

Checked-in idempotent SQL: `supabase-integration/migrations/002_phase2_issue_seed.sql`.

Creates / upserts:

- Two **published** `digest_issues` (№14 current from mock.js + №13 past for archive)
- Ready `materials` with Playwright slugs (`rag-systems`, …) + tags/relations
- `digest_issue_items` TOC positions
- One `voting_cycles` row (open window 3–16 Apr 2026) when missing

**Apply once on the shared VM** (`knowledge-db.ru`):

1. Prefer Supabase MCP / Studio SQL / `psql` — execute the file as **insert/upsert only**.
2. Or non-interactive CLI when `SUPABASE_ACCESS_TOKEN` is set: `supabase db push` (or Cloud.ru-documented remote equivalent) from repo root.
3. Re-running the file is safe (`ON CONFLICT` on `number` / `slug`; voting cycle uses `WHERE NOT EXISTS`).

**Do not** `TRUNCATE` / `DELETE` wipe / `db reset` on the shared VM. No `cover_url` / `is_current` columns (D-24/D-26).

**Verify after apply:**

```sql
select count(*) from digest_issues where published_at is not null;  -- expect >= 2
select slug from materials where slug = 'rag-systems';             -- expect 1 row
select count(*) from voting_cycles;                                -- expect >= 1
```

Record the apply method in the operator resume signal (or append a one-line note below when confirmed).

**Applied (2026-09-20):** Supabase MCP PostgREST `insert` (service_role) — `raw_sql` unavailable without `POSTGRES_URL`. Verified: published issues=2 (№13, №14), materials=6 (incl. `rag-systems`), voting_cycles=1 (open).

---

## 4c. Phase 3 voting ballot seed + open-cycle trigger (VOTE-01/03/04)

Checked-in idempotent SQL: `supabase-integration/migrations/003_phase3_voting_ballot.sql`.

Creates / upserts (option-a — trigger + use-case):

- `BEFORE INSERT OR UPDATE` trigger `votes_enforce_open_and_topic` — rejects writes when `voting_cycles.status != 'open'` or `topics.cycle_id != votes.cycle_id`
- ≥3 `topics` on the open Phase 2 cycle (titles from `mock.js` votingTopics: LLM / RAG / AutoML) with audit-language `description`
- `topic_materials` links for LLM + RAG only — **AutoML has zero materials** (VOTE-04 «0 материалов»)
- Index `votes_cycle_id_topic_id_idx` for tallies

**Apply once on the shared VM** (`knowledge-db.ru`) **after** Phase 2 seed (open cycle must exist):

1. Prefer non-interactive CLI when `SUPABASE_ACCESS_TOKEN` is set: `supabase db push` (or Cloud.ru-documented remote equivalent) from repo root.
2. If CLI cannot reach the shared VM: apply the SQL file once via Supabase MCP / Studio SQL / `psql` — **insert/upsert + DDL for function/trigger only**; do not reset DB.
3. Re-running the file is safe (`CREATE OR REPLACE` / `DROP TRIGGER IF EXISTS` / `WHERE NOT EXISTS` on topic names / `ON CONFLICT DO NOTHING` for topic_materials).

**Do not** `TRUNCATE` / `DELETE` wipe / `db reset` on the shared VM. Never expose `SUPABASE_SECRET_KEY` via `VITE_`.

**Verify after apply:**

```sql
-- expect >= 3 topics on an open cycle
select t.name, count(tm.material_id) as materials_count
from topics t
join voting_cycles vc on vc.id = t.cycle_id and vc.status = 'open'
left join topic_materials tm on tm.topic_id = t.id
group by t.id, t.name
order by t.name;
-- expect AutoML row with materials_count = 0
-- expect RAG title present

select tg.tgname
from pg_trigger tg
join pg_class c on c.oid = tg.tgrelid
where c.relname = 'votes' and not tg.tgisinternal;
-- expect votes_enforce_open_and_topic
```

Record the apply method in the operator resume signal (or append a one-line note below when confirmed).

**Applied (2026-09-20):** Seed via Supabase MCP PostgREST `insert` (service_role) — 3 topics on `cycle_id=1` (LLM id=1 materials=3, RAG id=2 materials=5, AutoML id=3 materials=0). DDL (`votes_enforce_open_and_topic` function/trigger + `votes_cycle_id_topic_id_idx`) via Studio SQL — operator confirmed `Success. No rows returned`. `raw_sql`/CLI `db push` unavailable without `POSTGRES_URL` / access token path.

---

## 4d. Phase 4 knowledge chunks + razbory seed (KNOW-01…03, RAZB-01…04)

Checked-in idempotent SQL: `supabase-integration/migrations/004_phase4_knowledge_razbory.sql`.

Creates / upserts (apply **after** Phase 2 materials + Phase 3 topics):

- `search_knowledge_chunks(...)` RPC — hybrid vector (`<=>`) + FTS (`ts_rank_cd`), ready-only, optional `role_filter`, material dedupe; **SECURITY INVOKER**; execute granted to `service_role` only
- ≥4 `knowledge_chunks` rows (1024-d embeddings via deterministic `StubQueryEmbedder` algorithm) spanning **ds** (`pgvector`, `rag-systems`) and **analyst** (`anomaly-detection`, `sql-dashboards`) ready materials
- ≥1 **published** multi-section razbor with metrics table + `notebook_path = hybrid-retrieval.ipynb` (relative to `NOTEBOOK_ROOT`)
- ≥1 **announcement** stub (empty body)
- ≥1 **published overview** razbor without a metrics/quality table

**Apply once on the shared VM** (`knowledge-db.ru`) **after** Phase 2–3 seeds (ready materials + topics must exist):

1. Prefer non-interactive CLI when `SUPABASE_ACCESS_TOKEN` is set: `supabase db push` (or Cloud.ru-documented remote equivalent) from repo root.
2. If CLI cannot reach the shared VM: apply the SQL file once via Supabase MCP / Studio SQL / `psql` — **insert/upsert + CREATE OR REPLACE function only**; do not reset DB.
3. Re-running the file is safe (`ON CONFLICT` on `(material_id, chunk_index)`; razbor inserts use `WHERE NOT EXISTS` on `(topic_id, title)`).

**Notebook file on the API host:** copy `design-frontend/assets/notebooks/hybrid-retrieval.ipynb` into the directory pointed to by `NOTEBOOK_ROOT` (env for live FastAPI). Seeded `notebook_path` is the basename `hybrid-retrieval.ipynb` — resolved under that root by `LocalNotebookStorage`.

**Do not** `TRUNCATE` / `DELETE` wipe / `db reset` on the shared VM. Never expose `SUPABASE_SECRET_KEY` via `VITE_`. Live search must use this RPC/SQL path — not `list_all` + Python cosine.

**Verify after apply:**

```sql
select count(*) from knowledge_chunks;  -- expect >= 1 (seed targets >= 4)
select count(*) from razbors where status = 'published';  -- expect >= 2
select count(*) from razbors where status = 'announcement';  -- expect >= 1
select proname from pg_proc where proname = 'search_knowledge_chunks';  -- expect 1
```

Also confirm the notebook file exists at `$NOTEBOOK_ROOT/hybrid-retrieval.ipynb` on the API host.

Record the apply method in the operator resume signal (or append a one-line note below when confirmed).

**Applied:** 2026-09-21 — operator confirmed: SQL for `004_phase4_knowledge_razbory.sql` applied on shared VM (checkpoint steps 1, 2, 4); notebook copied to `NOTEBOOK_ROOT` (`hybrid-retrieval.ipynb` present); `NOTEBOOK_ROOT` set in `.env` for local API. Operator confirmed verify queries; exact row counts not logged in the resume signal.

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
