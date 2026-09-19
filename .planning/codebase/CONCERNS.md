# Codebase Concerns

**Analysis Date:** 2026-09-19

## Tech Debt

**Frontend still mock-only (no live API):**
- Issue: React delivery in `web/` reads static fixtures and a fake vote API; nothing calls backend or Supabase.
- Files: `web/src/data/mock.js`, `web/src/services/votingApi.js`, `web/src/pages/IssuePage.jsx`, `web/src/pages/MaterialPage.jsx`, `web/src/pages/KnowledgePage.jsx`, `web/src/pages/VotingPage.jsx`
- Impact: Homework UI can demo flows, but production auth, persistence, hybrid search, and voting integrity are not wired. E2E (`tests/web-app.spec.js`) only validates mock behavior.
- Fix approach: Introduce `web/src/services/` clients against FastAPI (or Supabase via backend), keep mocks behind a clear test harness, migrate pages one route at a time under TDD.

**Composition root wires in-memory adapters as the default app:**
- Issue: `build_in_memory_container()` is the only builder; comment admits Supabase adapters are not connected.
- Files: `backend/src/backend/composition/container.py`, `backend/src/backend/tests_support/in_memory.py`
- Impact: Domain use-cases exist but cannot run against real Postgres/pgvector without new adapters and a second composition path.
- Fix approach: Implement repository adapters in `supabase-integration/`, add `build_supabase_container()` (or env-selected factory) in `backend/.../composition/`, keep in-memory for unit tests only.

**`supabase-integration` is schema-only:**
- Issue: Public API exposes only `migrations_dir()`; no Supabase SDK client, no port implementations, no package dependency on `supabase`.
- Files: `supabase-integration/src/supabase_integration/__init__.py`, `supabase-integration/pyproject.toml`, `supabase-integration/migrations/001_initial_schema.sql`
- Impact: ADR-0004’s “swap adapter without touching domain” cannot happen yet; schema and application layer are disconnected.
- Fix approach: Add typed adapters implementing `MaterialRepository` / `KnowledgeChunkRepository` (and later voting/ingestion ports); wire secrets only in composition.

**`data-collection` is DTO-only:**
- Issue: YouTube / FoundryModels / text-import modules define Pydantic DTOs only; no HTTP clients, retries, or error mapping to domain errors.
- Files: `data-collection/src/data_collection/dto/youtube.py`, `data-collection/src/data_collection/dto/foundry.py`, `data-collection/src/data_collection/dto/text_import.py`, `data-collection/pyproject.toml`
- Impact: Ingestion pipeline and embeddings cannot run; FoundryModels (ADR-0002) remains a paper dependency.
- Fix approach: Add ports for transcript/summary/tag/embed, implement Cloud.ru clients behind them, map SDK failures at the adapter boundary.

**Missing HTTP delivery layer:**
- Issue: Architecture docs prescribe FastAPI routers under `backend/.../interface/http/`; that tree does not exist. Backend package has zero runtime dependencies (`backend/pyproject.toml`).
- Files: `backend/` (no `interface/`), `.cursor/rules/architecture.mdc` (expected layout), `backend/README.md`
- Impact: Frontend and external callers have no authenticated API surface; use-cases are library-only.
- Fix approach: Add thin FastAPI routers + DI from composition; do not put business rules in routers.

**Dual frontend surfaces:**
- Issue: Static prototype `design-frontend/` (including god-script `design-frontend/scripts/app.js`, ~649 lines) coexists with React `web/`. Spec says design-frontend remains the mockup reference; React is the deliverable.
- Files: `design-frontend/`, `web/`, `docs/digest-cds/technical_specification.md` (§3.3), `package.json` (`serve:design`, `test:design`)
- Impact: Feature drift risk (razbory/admin screens exist in HTML but not in React routes). Agents may edit the wrong tree.
- Fix approach: Treat `design-frontend/` as read-only reference; all product changes land in `web/` first; eventually archive or freeze the static tree.

**Manual schema apply, no migrate tooling / local Compose:**
- Issue: Migrations are applied via Studio SQL Editor; no Docker Compose, Dockerfile, or migrate CLI in-repo.
- Files: `supabase-integration/README.md`, `docs/adr/0004-self-hosted-supabase-on-vm.md`
- Impact: Local/staging parity is fragile; schema drift between `knowledge-db.ru` and `001_initial_schema.sql` is hard to detect.
- Fix approach: Add Compose for Postgres+pgvector (or Supabase stack) and a scripted migrate path; keep migration files as source of truth.

**ID / role model inconsistencies across layers:**
- Issue: Web mocks use string material IDs/slugs (`'rag-systems'`); domain/DB use `bigint` identities and `slug`. Domain `related_material_ids` is `tuple[str, ...]` while `material_relations` uses bigint FKs. UI/DTO role hint `'sva'` vs DB `app_role` enum `'employee' | 'analyst' | 'ds' | 'admin'`.
- Files: `web/src/data/mock.js`, `backend/src/backend/domain/material.py`, `data-collection/src/data_collection/dto/foundry.py` (`RoleHint`), `supabase-integration/migrations/001_initial_schema.sql`
- Impact: Adapter mapping will be error-prone; filters and RLS role checks can silently disagree.
- Fix approach: Lock a single role vocabulary and ID strategy in domain DTOs; map `'sva'` → `'employee'` (or rename enum) in one place; use slug for URLs and int IDs internally.

## Known Bugs

**Knowledge UI search ≠ knowledge use-case:**
- Symptoms: `KnowledgePage` keyword-filters mock cards client-side; backend `search_knowledge` does hybrid vector+token scoring over chunks — never called from UI.
- Files: `web/src/pages/KnowledgePage.jsx`, `web/src/utils/filters.js`, `backend/src/backend/application/use_cases/search_knowledge.py`
- Trigger: Any expectation that “база знаний” uses pgvector/FTS.
- Workaround: Demo with mock keywords only; do not claim semantic search in production until wired.

**Vote confirmation is ephemeral:**
- Symptoms: Confirmed vote lives in React state; refresh clears it. `submitVote` always “succeeds” after `delay()` unless fail-once harness is armed.
- Files: `web/src/pages/VotingPage.jsx`, `web/src/services/votingApi.js`
- Trigger: Reload after confirm; multi-tab; real cycle open/close.
- Workaround: Demo URL `?simulateError=1` for error UX only.

**React app missing screens present in prototype / acceptance criteria:**
- Symptoms: No routes for разборы or admin shortlist; `App.jsx` only has issue/voting/knowledge/materials.
- Files: `web/src/App.jsx`, `design-frontend/pages/razbory.html`, `design-frontend/pages/admin-digest.html`, `docs/digest-cds/acceptance_criteria.md`
- Trigger: Navigating expected product IA from backlog/spec.
- Workaround: Use `design-frontend/` for those screens as static demos only.

## Security Considerations

**RLS incomplete for product reads/writes:**
- Risk: RLS is enabled on all 18 tables, but policies cover only a subset (`materials`/`knowledge_chunks` ready SELECT, digest SELECT, own votes R/W, own profile SELECT). Authenticated clients cannot SELECT `topics`, `voting_cycles`, `material_tags`, `razbors`, etc.; pipeline writes assume `service_role` bypass with no adapter yet enforcing key discipline.
- Files: `supabase-integration/migrations/001_initial_schema.sql` (RLS section ~240–297), `supabase-integration/README.md`
- Current mitigation: Default-deny for anon on tables without policies; Studio-applied RLS noted in ADR-0004.
- Recommendations: Add least-privilege policies for ballot/topics/tags/razbors; never expose service role to the browser; put privileged writes behind backend composition.

**Votes updatable without cycle-status guard:**
- Risk: `votes_update_own` allows UPDATE of own row with no check that `voting_cycles.status = 'open'` or that `topic_id` belongs to `cycle_id`.
- Files: `supabase-integration/migrations/001_initial_schema.sql` (`votes` table PK `(cycle_id, user_id)`, policies)
- Current mitigation: One row per user per cycle at PK level; UI does not yet hit DB.
- Recommendations: Policy/trigger enforcing open cycle + topic∈cycle; prefer server use-case for vote submit.

**Auth and domain restriction not implemented in app:**
- Risk: ADR-0003 requires `@sberbank.ru` / `@omega.sbrf.ru` signup; React app has no login, no Supabase Auth, no domain gate.
- Files: `docs/adr/0003-email-domain-restriction.md`, `web/src/App.jsx` (no auth routes)
- Current mitigation: Spec allows mock for homework UI; self-hosted Auth exists only as platform capability.
- Recommendations: Wire Auth via backend or Supabase Auth hook/config; reject non-allowed domains at signup; protect all data routes.

**Secrets file present locally:**
- Risk: `.env` exists at repo root (gitignored). Accidental commit or logging would leak Supabase/API keys.
- Files: `.env` (existence only — contents not inspected), `.gitignore`
- Current mitigation: `.env` / `.env.*` listed in `.gitignore`.
- Recommendations: Keep secrets out of docs/commits; use MaskMCP/CI secrets; document required var *names* only in `.env.example` without values.

**Self-hosted Supabase attack surface:**
- Risk: Per ADR-0004, team owns backups, updates, and endpoint hardening for `knowledge-db.ru`; misconfigured anon key or open Studio increases exposure.
- Files: `docs/adr/0004-self-hosted-supabase-on-vm.md`
- Current mitigation: Architectural intent to encapsulate access in `supabase-integration`.
- Recommendations: Network restrict Studio/API, rotate keys, monitor RLS regressions with policy tests.

## Performance Bottlenecks

**In-process hybrid search loads all chunks:**
- Problem: `search_knowledge` iterates `chunks.list_all()`, computes cosine in Python, and approximates FTS with substring token hits — ignoring `knowledge_chunks` HNSW and `content_tsv` GIN indexes.
- Files: `backend/src/backend/application/use_cases/search_knowledge.py`, `backend/src/backend/application/ports/knowledge_chunk_repository.py` (`list_all`), `supabase-integration/migrations/001_initial_schema.sql` (indexes)
- Cause: Port shaped for in-memory fakes, not vector/FTS queries.
- Improvement path: Replace `list_all` with a `search(...)` port implemented in SQL (`<=>` + `ts_rank`); keep Python hybrid only for unit fakes.

**Client-side knowledge pagination is fake delay:**
- Problem: “Загрузить ещё” uses `delay()` then expands the full filtered list; no server pagination.
- Files: `web/src/pages/KnowledgePage.jsx`, `web/src/utils/delay.js`
- Cause: Prototype UX.
- Improvement path: Cursor/limit API once backend search exists.

## Fragile Areas

**Schema contract tests are string presence checks:**
- Files: `tests/unit/test_schema_migration_contract.py`
- Why fragile: Renames, broken policies, or missing indexes can still “pass” if substrings remain; no live DB apply.
- Safe modification: Change migration then update contract assertions; add integration migrate+query job before trusting prod.
- Test coverage: Unit contract only; no RLS/policy tests.

**Embedding dimension locked before model locked:**
- Files: `data-collection/src/data_collection/dto/foundry.py` (`EMBEDDING_DIM = 1024`), migration `vector(1024)`, comments in SQL/DTO
- Why fragile: Changing FoundryModels embedding size requires coordinated migration + DTO + reindex of all chunks.
- Safe modification: Confirm model ID in ADR/spec before writing production embeddings; plan alter+reembed runbook.
- Test coverage: DTO length validator only (`tests/unit/test_foundry_dtos.py`).

**`design-frontend/scripts/app.js` monolith:**
- Files: `design-frontend/scripts/app.js`
- Why fragile: Large imperative script shared across static pages; easy regressions when syncing UX to React.
- Safe modification: Prefer implementing behavior in `web/`; treat static JS as reference.
- Test coverage: Playwright `tests/design-frontend.spec.js` (separate project).

**Ports too thin for product features:**
- Files: `backend/src/backend/application/ports/material_repository.py`, `knowledge_chunk_repository.py`
- Why fragile: No ports yet for votes, issues, shortlist, ingestion, profiles; new features risk leaking SDK into use-cases.
- Safe modification: Add Protocol first + in-memory fake + failing test before adapters (TDD / architecture rules).
- Test coverage: Publish/index/search covered; voting/ingestion not.

## Scaling Limits

**Knowledge retrieval:**
- Current capacity: Suitable for tiny in-memory chunk sets used in unit tests.
- Limit: Full-table `list_all` + Python cosine breaks as chunk count grows; also duplicates work already paid for by HNSW/FTS.
- Scaling path: DB-side hybrid search; optional ANN params / partition by material status.

**Activity / leaderboard:**
- Current capacity: `activity_events` table exists; no writers/readers in application code. Leaderboard deferred (ADR-0001).
- Limit: Unbounded inserts without retention once instrumentation ships.
- Scaling path: Batch ingest, indexes already on `user_id`/`created_at`; define retention before enabling UI.

## Dependencies at Risk

**FoundryModels (Cloud.ru):**
- Risk: External ML pipeline dependency for transcript/summary/tags/embeddings (ADR-0002); no client code yet, only DTOs.
- Impact: Ingestion and indexing blocked; outages need NFR handling not implemented.
- Migration plan: Keep ports stable; swap provider adapter if Cloud.ru unavailable.

**Supabase client not yet a dependency:**
- Risk: `supabase-integration` depends only on `backend`; no official SDK pinned.
- Impact: When added, version/API choices affect all adapters at once.
- Migration plan: Pin SDK in that package only; never import from domain/use-cases.

**No CI pipeline:**
- Risk: No `.github/` workflows detected; quality depends on local `npm test` / `uv run pytest`.
- Impact: Broken main can land unnoticed; Playwright browsers install is postinstall-local.
- Migration plan: Add CI for unit + Playwright web project; gate PRs.

## Missing Critical Features

**End-to-end product spine:**
- Problem: No auth, no HTTP API, no Supabase adapters, no Foundry/YouTube collectors, no email digest send, no admin shortlist UI in React, no разборы routes, no activity event writers.
- Blocks: Real СВА deployment beyond homework demo; acceptance criteria that assume backend persistence and hybrid search.

**Local/prod parity tooling:**
- Problem: No Docker Compose/Dockerfile for app+DB; migrate-by-Studio only.
- Blocks: Repeatable onboarding and staging verification.

## Test Coverage Gaps

**No adapter / integration / RLS tests:**
- What's not tested: Live Supabase queries, RLS deny/allow matrices, Foundry/YouTube HTTP, FastAPI routes (absent).
- Files: `tests/unit/*` (domain/DTO/composition/SQL string contract), `tests/web-app.spec.js` (mock UI)
- Risk: Production schema/policies can diverge; adapters can violate ports unnoticed.
- Priority: High (before connecting real credentials)

**Voting and knowledge product rules untested against persistence:**
- What's not tested: One vote per open cycle with topic∈cycle; hybrid search ranking vs pgvector; publish→index→search pipeline on DB.
- Files: `tests/unit/test_publish_and_index.py`, `tests/unit/test_search_knowledge.py` (in-memory only)
- Risk: Green unit suite with broken production path.
- Priority: High

**Auth / domain restriction:**
- What's not tested: Signup domain gate (ADR-0003), role-based UI/API.
- Files: Not present in `web/` or `backend/`
- Risk: Open registration or wrong-role data leaks once Auth is enabled without tests.
- Priority: High (when Auth is introduced)

**Admin / razbor / shortlist:**
- What's not tested: Flows exist in design acceptance docs and static HTML only.
- Files: `docs/digest-cds/acceptance_criteria.md`, `design-frontend/pages/`
- Risk: Shipping React without those screens leaves major US gaps.
- Priority: Medium (post homework / toward v1)

---

*Concerns audit: 2026-09-19*
