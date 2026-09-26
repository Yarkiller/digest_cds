---
last_mapped_commit: 427615dc0eb6b133900513db4b0f240398db862f
---
<!-- refreshed: 2026-09-26 -->
# External Integrations

**Analysis Date:** 2026-09-26

## APIs & External Services

**Self-hosted Supabase (primary runtime integration):**
- PostgREST + Auth on `https://knowledge-db.ru/` (configurable; ADR-0004)
  - Python SDK: `supabase` 2.31.0 via `supabase_integration.client` (`create_service_role_client` / `create_publishable_client`)
  - JS SDK: `@supabase/supabase-js` 2.116.0 — browser Auth only (`web/src/services/supabaseClient.js` → `authApi.js`)
  - Auth: `SUPABASE_URL` + `SUPABASE_SECRET_KEY` (server/service_role, composition only); publishable key for SPA (`VITE_SUPABASE_*`); JWKS for FastAPI JWT (`SUPABASE_JWKS_URL`, `SUPABASE_JWT_ISSUER`)
  - Wiring: `APP_CONTAINER=live` → `backend/composition/live.py`; default `memory` keeps unit tests offline

**ML / content pipeline (Cloud.ru) — planned, DTO-only today:**
- FoundryModels (Cloud.ru) — transcription/import assist, summarization, tagging, embeddings (dim 1024), article assist
  - SDK/Client: **not installed**; contract DTOs in `data-collection/src/data_collection/dto/foundry.py`
  - Auth: env/secrets on Cloud.ru VM (ADR-0002); no Foundry env vars in `.env.example` yet
  - Decision: ADR-0002 — no public foreign LLM/Whisper APIs; no local Whisper on app VM
  - Runtime stand-in: `StubQueryEmbedder` in live composition (knowledge search embeddings)

**External content sources — planned, DTO-only today:**
- YouTube Data API / captions — ingestion metadata (`YoutubeSourceDto` in `data-collection/.../dto/youtube.py`)
  - SDK/Client: **not installed**
  - Tests: `tests/unit/test_youtube_source_dto.py`
- Manual text / URL import — `TextImportDto` (`source_system = "text_import"`)

**Email:**
- Corporate Sber SMTP — production digest delivery (spec / ADR path)
  - v1 runtime: `StubMailer` (`MAILER=stub`) — persists send audit with `delivery_status='stubbed'`; logs body; no network SMTP
  - `SmtpMailer` exists but raises `NotImplementedError`; `MAILER=smtp` **fails fast at startup**
  - Auth VM GoTrue: autoconfirm enabled for self-service `/register` (SMTP for confirmation mail is ops-deferred; see runbook §4.1)

**Frontend ↔ Backend HTTP:**
- FastAPI base URL via `VITE_API_BASE_URL` (default `http://127.0.0.1:8000`)
- Service modules: `contentApi`, `meApi`, `votingApi`, `knowledgeApi`, `razboryApi`, `adminApi` under `web/src/services/`
- Cutover: `VITE_USE_MOCKS` — `true` (default / Playwright) uses mocks; `false` hits live API (never silent mock fallback on live errors)

## Data Storage

**Databases:**
- Self-hosted Supabase (PostgreSQL + **pgvector** + **pg_trgm**) on a separate VM via Docker Compose
  - Connection: `SUPABASE_URL` + keys from env (documented instance `https://knowledge-db.ru/`)
  - Client: `supabase-py` adapters implementing backend ports (profiles, issues, materials, votes, knowledge chunks, razbors, shortlist, digest publisher, ping recorder)
  - Migrations: `supabase-integration/migrations/`
    - `001_initial_schema.sql` — 18 `public` tables; RLS enabled; embedding `vector(1024)`
    - `002`–`006` — phase seeds, voting ballot, knowledge/razbory, admin shortlist, claim/publish RPC
  - Live apply: Studio SQL Editor / ops on VM (see `supabase-integration/README.md`); contracts in `tests/unit/test_*_contract.py` and migration tests
  - Composition: `build_in_memory_container` vs `build_live_container`

**Tables by layer (migration 001):**
- Auth profile: `profiles` → `auth.users`
- Ingestion: `ingestion_sources`, `ingestion_jobs`, `source_texts`
- Publication: `materials`, `material_tags`, `material_relations`
- Digest: `digest_issues`, `digest_issue_items`, `digest_shortlist_batches`, `digest_shortlist_items`
- Knowledge: `knowledge_chunks`
- Voting / разбор: `voting_cycles`, `topics`, `topic_materials`, `votes`, `razbors`
- Activity: `activity_events`

**File Storage:**
- Supabase Storage planned as part of self-hosted stack (ADR-0004) — **no Storage adapter** in repo yet
- Local notebooks: `NOTEBOOK_ROOT` + `LocalNotebookStorage` for authenticated `.ipynb` FileResponse (`/razbory/...`)
- Local static assets: `web/public/`, `design-frontend/assets/`

**Caching:**
- None detected (no Redis)

## Authentication & Identity

**Auth Provider:**
- Supabase Auth (self-hosted GoTrue) — production identity; `profiles.id` FK to `auth.users`
  - SPA: publishable-client `signInWithPassword` / `signUp` only — never `service_role` in the browser
  - FastAPI: Bearer JWT verified ES256 via JWKS (`audience=authenticated`); corporate email domain check (`ALLOWED_EMAIL_DOMAINS` or default `@sberbank.ru`, `@omega.sbrf.ru` — ADR-0003)
  - First successful `GET /me` upserts `profiles` via `ProfileRepository.get_or_upsert`
  - Admin: `app_role` / claim checks for `/admin/*` (403 for non-admin)
  - Token storage: Supabase JS session (browser); API calls send `Authorization: Bearer …`
  - Mock path: `VITE_USE_MOCKS≠false` — `RequireAuth` bypass / mock session (Playwright offline)

**OAuth Integrations:**
- None (email/password only)

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry/Datadog/etc. in dependencies)

**Analytics:**
- None

**Logs:**
- Backend: `structlog` JSON to stdout with `request_id` (`RequestIdMiddleware`, CORS allow header `X-Request-ID`)
- Spec also calls for structured admin audit + correlatable ops logs — partial via `activity_events` / shortlist send audit; full NFR-L* ops stack not implemented
- Playwright / pytest console for local verification

## CI/CD & Deployment

**Hosting:**
- Target: Cloud.ru application VM + separate Supabase VM (ADR-0002, ADR-0004)
- Local proof path: Vite + Uvicorn against remote `knowledge-db.ru` (`docs/agents/local-platform-runbook.md`)
- GitHub remote referenced in `README.md`: `https://github.com/Yarkiller/digest_cds`
- No Dockerfile / compose for the app in-repo (Supabase Compose lives on its VM per ADR)

**CI Pipeline:**
- None detected — no `.github/workflows/` present
- Local gates: `npm test` (Playwright), `npm run test:unit` / `uv run pytest`

## Environment Configuration

**Required env vars (names only — never commit values):**

| Layer | Variables |
|-------|-----------|
| Backend / Supabase | `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `SUPABASE_JWKS_URL`, `SUPABASE_JWT_ISSUER` |
| Backend / HTTP | `API_CORS_ORIGINS`, `ALLOWED_EMAIL_DOMAINS`, `APP_CONTAINER` (`memory`\|`live`), `NOTEBOOK_ROOT`, `MAILER` (`stub`\|`smtp`) |
| Vite (publishable only) | `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_API_BASE_URL`, `VITE_USE_MOCKS` |

**Secrets location:**
- Repo-root `.env` (gitignored); template `.env.example`
- `web/.env.local` (gitignored) for Vite live proof
- `.cursor/mcp.json` gitignored (agent MCP credentials)
- Production: Cloud.ru / VM secret store (NFR-S3)
- Agent secret tooling via Mask MCP (`mask_list_secrets` / `mask_fetch`) — not part of app runtime

**Do not use:**
- Hardcoded `knowledge-db.ru` or keys in domain/application layers — adapter + env only (ADR-0004)
- `SUPABASE_SECRET_KEY` behind any `VITE_` prefix

**Mock/stub services:**
- In-memory repositories (`APP_CONTAINER=memory`)
- `VITE_USE_MOCKS=true` frontend harnesses
- `StubMailer`, `StubQueryEmbedder`

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected (digest send is stubbed persistence + log; no webhook publishers)

## HTTP surface (internal API, not third-party)

| Prefix | Role |
|--------|------|
| `GET /health` | Liveness |
| `/me`, `/me/ping`, PATCH display name | Authenticated profile / activity |
| `/issues`, archive routes | Current + archived digest issues |
| `/materials/{id}` | Material detail |
| `/knowledge` | Hybrid knowledge search |
| `/razbory` | Notebook разборы list/detail/download |
| `/voting` | Voting cycle + ballot submit |
| `/admin/*` | Shortlist triage, email preview, stub send/publish |

## Integration Boundaries (how to extend)

| Concern | Module / path | Pattern |
|---------|---------------|---------|
| Ports (interfaces) | `backend/src/backend/application/ports/` | `Protocol` / ABC |
| Use-cases | `backend/src/backend/application/use_cases/` | Depend only on domain + ports |
| Wiring | `backend/src/backend/composition/` (`container.py`, `live.py`, `settings.py`) | Composition root — swap memory ↔ Supabase here |
| External DTOs | `data-collection/src/data_collection/dto/` | Normalize YouTube / Foundry / text import at the boundary |
| DB schema / SDK adapters | `supabase-integration/` | Migrations + repository adapters |
| Frontend API | `web/src/services/` | UI must not import Supabase SDK outside `supabaseClient.js` / auth path |

**Public exports:**
- `data-collection` — DTO barrel (`YoutubeSourceDto`, Foundry result DTOs, `TextImportDto`, `EMBEDDING_DIM`)
- `supabase-integration` — client factories + repository / publisher adapters

## Agent / Developer Tooling Integrations (not product runtime)

- Supabase MCP (`project-0-Digital_CDS-supabase`) — schema/query against live DB for agents
- Context7 MCP — library docs
- Playwright MCP / Chrome DevTools — browser automation for agents
- Skills under `.agents/skills/supabase/` and `supabase-postgres-best-practices/` — Postgres/RLS guidance when changing schema

---

*Integration audit: 2026-09-26*
*Update when adding/removing external services*
