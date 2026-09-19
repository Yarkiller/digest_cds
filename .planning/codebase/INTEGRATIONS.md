# External Integrations

**Analysis Date:** 2026-09-19

## APIs & External Services

**ML / content pipeline (Cloud.ru):**
- FoundryModels (Cloud.ru) — transcription/import assist, summarization, tagging, embeddings (dim 1024), article assist
  - SDK/Client: **not installed**; contract DTOs only in `data-collection/src/data_collection/dto/foundry.py` (`TranscriptResultDto`, `SummaryResultDto`, `TaggingResultDto`, `EmbeddingResultDto`, `ArticleAssistDto`, `EMBEDDING_DIM = 1024`)
  - Auth: env/secrets on Cloud.ru VM (ADR-0002); no env var names wired in application code yet
  - Decision: ADR-0002 — no public foreign LLM/Whisper APIs; no local Whisper on app VM

**External content sources:**
- YouTube Data API v3 — fetch source metadata for ingestion (video remains external; no media blobs stored)
  - SDK/Client: **not installed**; DTO `YoutubeSourceDto` in `data-collection/src/data_collection/dto/youtube.py`
  - Auth: YouTube API credentials (planned; not coded)
  - Tests: `tests/unit/test_youtube_source_dto.py`
- Manual text / URL import — `TextImportDto` in `data-collection/src/data_collection/dto/text_import.py` (`source_system = "text_import"`)

**Email:**
- Corporate Sber SMTP — weekly digest delivery (spec / backlog)
  - SDK/Client: **not implemented**
  - Auth: SMTP credentials in Cloud.ru / VM secrets (NFR-S3 in `docs/digest-cds/technical_specification.md`)

**Frontend API surface (current homework app):**
- No live backend HTTP client — UI uses `web/src/data/mock.js` and mock service `web/src/services/votingApi.js` (`submitVote` with artificial delay / fail harness)
- Architecture rule: future API calls must go through `web/src/services/` only

## Data Storage

**Databases:**
- Self-hosted Supabase (PostgreSQL + **pgvector** + **pg_trgm**) on a separate VM via Docker Compose
  - Connection: configurable base URL (documented instance `https://knowledge-db.ru/`); keys via env/secrets — ADR-0004
  - Client: **adapter module only** — `supabase-integration/` currently exposes `migrations_dir()` in `supabase-integration/src/supabase_integration/__init__.py`; no `create_client` / SDK dependency yet
  - Schema: `supabase-integration/migrations/001_initial_schema.sql` (18 `public` tables; RLS enabled; embedding `vector(1024)`)
  - Live apply: Studio SQL Editor (see `supabase-integration/README.md`); contract checked by `tests/unit/test_schema_migration_contract.py`
  - Composition today: in-memory repos via `backend/src/backend/composition/container.py` (`build_in_memory_container`)

**Tables by layer (migration):**
- Auth profile: `profiles` → `auth.users`
- Ingestion: `ingestion_sources`, `ingestion_jobs`, `source_texts`
- Publication: `materials`, `material_tags`, `material_relations`
- Digest: `digest_issues`, `digest_issue_items`, `digest_shortlist_batches`, `digest_shortlist_items`
- Knowledge: `knowledge_chunks`
- Voting / разбор: `voting_cycles`, `topics`, `topic_materials`, `votes`, `razbors`
- Activity: `activity_events`

**File Storage:**
- Supabase Storage planned as part of self-hosted stack (ADR-0004) — **no Storage adapter code** in repo
- Local static assets: `web/public/`, `design-frontend/assets/` (covers, notebooks references)

**Caching:**
- None detected

## Authentication & Identity

**Auth Provider:**
- Supabase Auth (self-hosted) — planned production identity; `profiles.id` FK to `auth.users`
  - Implementation: RLS policies in `001_initial_schema.sql` for `authenticated` role; pipeline writes via `service_role` (bypasses RLS)
  - Domain restriction (ADR-0003): registration/login only `@sberbank.ru` and `@omega.sbrf.ru` (fixed config list)
  - Frontend login / session wiring: **not in** current React SPA routes (`web/src/App.jsx` has no auth gate)

**Current local UI:**
- Unauthenticated mock SPA — no Supabase JS client, no session cookies

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry/Datadog/etc. in dependencies)

**Logs:**
- Spec requires structured admin audit + correlatable ops logs (NFR-L* in `docs/digest-cds/technical_specification.md`) — **not implemented** in application code
- Playwright / pytest console output for local verification only

## CI/CD & Deployment

**Hosting:**
- Target: Cloud.ru application VM + separate Supabase VM (ADR-0002, ADR-0004)
- GitHub remote referenced in `README.md`: `https://github.com/Yarkiller/digest_cds`
- No Dockerfile / compose for the app detected in-repo (Supabase Compose lives on its VM per ADR)

**CI Pipeline:**
- None detected — no `.github/workflows/` present
- Local gates: `npm test` (Playwright), `npm run test:unit` / `uv run pytest`

## Environment Configuration

**Required env vars:**
- Not declared in code. Planned categories (store in `.env` / VM secrets; never commit):
  - Supabase URL + anon/publishable key + `service_role` (server-only)
  - FoundryModels API credentials / endpoint
  - YouTube Data API key / OAuth as chosen by adapter
  - SMTP host/port/user/password (digest)
  - Allowed email domains config (ADR-0003)

**Secrets location:**
- Repo-root `.env` (gitignored; existence only — do not read/commit)
- `.cursor/mcp.json` gitignored (agent MCP credentials)
- Production: Cloud.ru / VM secret store (NFR-S3)
- Agent secret tooling available via Mask MCP (`mask_list_secrets` / `mask_fetch`) for local agent workflows — not part of app runtime

**Do not use:**
- Hardcoded `knowledge-db.ru` or keys in domain/application layers — adapter + env only (ADR-0004)

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected (digest is SMTP push; no webhook publishers in code)

## Integration Boundaries (how to extend)

| Concern | Module / path | Pattern |
|---------|---------------|---------|
| Ports (interfaces) | `backend/src/backend/application/ports/` | `Protocol` — e.g. `material_repository.py`, `knowledge_chunk_repository.py` |
| Use-cases | `backend/src/backend/application/use_cases/` | Depend only on domain + ports |
| Wiring | `backend/src/backend/composition/container.py` | Composition root — swap in-memory for Supabase adapters here |
| External DTOs | `data-collection/src/data_collection/dto/` | Normalize YouTube / Foundry / text import at the boundary |
| DB schema / future SDK | `supabase-integration/` | Migrations now; SDK adapters later |
| Frontend API | `web/src/services/` | UI must not import Supabase or backend internals |

**Public exports:**
- `data-collection/src/data_collection/__init__.py` — DTO barrel
- `supabase-integration` — `migrations_dir()` only until adapters land

## Agent / Developer Tooling Integrations (not product runtime)

- Supabase MCP (`project-0-Digital_CDS-supabase`) — schema/query against live DB for agents
- Context7 MCP — library docs
- Playwright MCP / Chrome DevTools — browser automation for agents
- Skills under `.agents/skills/supabase/` and `supabase-postgres-best-practices/` — Postgres/RLS guidance when changing schema

---

*Integration audit: 2026-09-19*
