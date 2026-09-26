---
last_mapped_commit: 427615dc0eb6b133900513db4b0f240398db862f
---
<!-- refreshed: 2026-09-26 -->
# Codebase Concerns

**Analysis Date:** 2026-09-26

## Tech Debt

**Ingestion / Foundry / YouTube still DTO-only:**
- Issue: `data-collection` exposes Pydantic DTOs only; no HTTP clients, retries, or port implementations for captions/LLM/embed. v1.1 Phase 6+ is planned (`ingestion-service` CLI) but not shipped.
- Files: `data-collection/src/data_collection/dto/youtube.py`, `data-collection/src/data_collection/dto/foundry.py`, `data-collection/src/data_collection/dto/text_import.py`, `data-collection/README.md`, `.planning/PROJECT.md` (Active checklist)
- Impact: Admin shortlist depends on seeded/demo drafts; PIPE-01 ranking pipeline and ADR-0002 FoundryModels path are unrealized. Schema tables `ingestion_*` / `source_texts` have no application writers.
- Fix approach: Land Phase 6 ports/DTOs → CLI adapter writing drafts via existing Supabase material/shortlist adapters; keep domain free of SDKs.

**Live knowledge search uses StubQueryEmbedder, not FoundryModels:**
- Issue: `build_live_container()` wires `StubQueryEmbedder` (sha256→1024-d). Seeded chunk embeddings in migration 004 match the stub algorithm — semantic search is honesty-path, not production ML.
- Files: `backend/src/backend/composition/live.py`, `backend/src/backend/application/ports/query_embedder.py`, `supabase-integration/migrations/004_phase4_knowledge_razbory.sql`
- Impact: Replacing stub with a real embedder without reindexing yields nonsense rankings; claiming “pgvector semantic search” overstates capability.
- Fix approach: Add Foundry (or DeepSeek) `QueryEmbedder` adapter; reembed all chunks; keep stub for unit/demo only.

**Digest mail is stub-only; SMTP fails fast:**
- Issue: `resolve_mailer("smtp")` raises at startup; live send returns `delivery_status=stubbed` and logs body. Product “send” is editorial claim+publish honesty, not email delivery.
- Files: `backend/src/backend/infrastructure/stub_mailer.py`, `backend/src/backend/composition/settings.py` (`mailer`), `.planning/PROJECT.md` (Out of Scope)
- Impact: Operators may believe digests were emailed; recipients never receive mail.
- Fix approach: Implement SmtpMailer behind `Mailer` port with secrets in env; keep stub as default until verified.

**Default composition is in-memory; live is env-opt-in:**
- Issue: `APP_CONTAINER` defaults to `memory`; `VITE_USE_MOCKS` defaults to true. Misconfigured “prod-like” runs silently use fakes.
- Files: `backend/src/backend/composition/settings.py`, `backend/src/backend/interface/http/app.py` (`resolve_container`), `web/src/services/authEnv.js`, `.env.example`
- Impact: Green local demos that never touch Supabase; false confidence in adapters.
- Fix approach: Fail-fast when `APP_CONTAINER=live` missing secrets (already); document runbook as sole live path; consider refusing `memory` when `ENV=production`.

**Dual frontend surfaces still coexist:**
- Issue: Static prototype `design-frontend/` (incl. large `design-frontend/scripts/app.js`) coexists with React `web/`. Spec keeps design as mockup reference; React is deliverable.
- Files: `design-frontend/`, `web/`, `package.json` (`serve:design`, `test:design`), `docs/digest-cds/technical_specification.md`
- Impact: Feature drift; agents editing the wrong tree; duplicate Playwright projects.
- Fix approach: Treat `design-frontend/` as read-only; all product changes in `web/`; eventually archive static tree.

**Manual schema apply on shared VM; no Compose/migrate CLI for app DB:**
- Issue: Migrations `001`–`006` applied via Studio/MCP/`psql` “once”; no Docker Compose/Dockerfile for app+API; README still points at Studio for `001`.
- Files: `supabase-integration/README.md`, `docs/agents/local-platform-runbook.md`, `supabase-integration/migrations/*.sql`
- Impact: Shared `knowledge-db.ru` drift risk; destructive reset forbidden; `006` apply noted pending in runbook while code already calls new RPC signature.
- Fix approach: Versioned migrate checklist with applied stamps; optional local Postgres+pgvector for offline; never reset shared VM.

**Publishable Supabase client constructed but unused in live wiring:**
- Issue: `create_publishable_client(...)` runs when key present, result discarded; all adapters use `service_role`.
- Files: `backend/src/backend/composition/live.py`
- Impact: Dead construction; future user-scoped RLS path not exercised; service_role blast radius is the only live path.
- Fix approach: Either remove unused call or wire user-JWT clients for least-privilege reads.

**`list_all` remains on KnowledgeChunkRepository:**
- Issue: Port still requires `list_all()`; live search correctly uses RPC `search`, but `list_all` can dump entire embedding table via service_role.
- Files: `backend/src/backend/application/ports/knowledge_chunk_repository.py`, `supabase-integration/src/supabase_integration/knowledge_chunk_repository.py`
- Impact: Accidental use-case regression reintroduces O(n) Python hybrid search / full-table fetch.
- Fix approach: Deprecate/remove `list_all` from production adapters; keep only on in-memory fake if needed for tests.

**Role vocabulary split (`sva` vs `employee`):**
- Issue: Material `roles` / Foundry `RoleHint` include `'sva'`; `app_role` enum is `'employee'|'analyst'|'ds'|'admin'`. Knowledge filter allowlist is only `analyst|ds`.
- Files: `data-collection/src/data_collection/dto/foundry.py`, `supabase-integration/migrations/001_initial_schema.sql`, `backend/src/backend/application/use_cases/search_knowledge.py`, seed SQL in `002`/`004`
- Impact: Mapping bugs when ingestion writes roles; UI must never send `sva` as filter (already rejected).
- Fix approach: Document single glossary; map `sva`→audience tag on materials only; never conflate with `profiles.role`.

**Stale brownfield map docs relative to shipped v1:**
- Issue: Sibling `.planning/codebase/` docs (e.g. ARCHITECTURE notes on “adapters not connected”) can lag phases 1–5.
- Files: `.planning/codebase/ARCHITECTURE.md` (and peers), `.planning/PROJECT.md` (“Preserve codebase map”)
- Impact: Planners may re-open closed gaps (no HTTP, no adapters).
- Fix approach: Refresh all seven map docs together; treat CONCERNS as current debt source of truth after this refresh.

## Known Bugs

**Hybrid search RPC scores all chunks (no ANN prefilter):**
- Symptoms: `search_knowledge_chunks` CTE scans `knowledge_chunks` with `<=>` + `ts_rank` without HNSW/IVF candidate cut; fine for seed size, degrades as corpus grows.
- Files: `supabase-integration/migrations/004_phase4_knowledge_razbory.sql`
- Trigger: Corpus growth beyond demo seeds.
- Workaround: Seed-sized data only; add `ORDER BY embedding <=> query LIMIT k` / HNSW ops before hybrid blend.

**Vote tally path loads wide tables into Python:**
- Symptoms: `SupabaseVoteRepository.list_topics_with_counts` selects all `topic_materials` and cycle votes, then counts in process — correct but chatty.
- Files: `supabase-integration/src/supabase_integration/vote_repository.py`
- Trigger: Large topic graphs / many votes.
- Workaround: Acceptable for homework scale; replace with SQL `GROUP BY` / view.

**Vote CAS timestamp format fragility:**
- Symptoms: Upsert CAS retries alternate ISO forms (`Z` vs `+00:00`) because PostgREST/timestamptz string equality is brittle — empty update → `VoteConflictError`.
- Files: `supabase-integration/src/supabase_integration/vote_repository.py` (`upsert_vote`)
- Trigger: Cross-client timestamp serialization differences.
- Workaround: Dual-format retry already present; prefer DB-side CAS RPC long-term.

**Migration 006 vs shared VM apply lag:**
- Symptoms: Python `SupabaseDigestPublisher` expects `claim_and_publish_digest(..., p_material_ids)`; runbook marks 006 apply as pending.
- Files: `supabase-integration/migrations/006_claim_publish_material_ids.sql`, `supabase-integration/src/supabase_integration/digest_publisher.py`, `docs/agents/local-platform-runbook.md`
- Trigger: Live admin send against VM without 006.
- Workaround: Apply 006 once via Studio/`psql` before live publish UAT; confirm RPC signature.

**Default mock SPA can mask live regressions:**
- Symptoms: Playwright honesty suites and default Vite env run under `VITE_USE_MOCKS=true`; live FE↔BE smoke remains human-gated.
- Files: `web/src/services/authEnv.js`, `tests/*.spec.js`, `.planning/PROJECT.md` (Known debt)
- Trigger: CI/local green while live wiring broken.
- Workaround: Explicit runbook live proof (`VITE_USE_MOCKS=false` + `APP_CONTAINER=live`).

## Security Considerations

**Service-role backend bypasses RLS for all product I/O:**
- Risk: Live adapters use `create_service_role_client`; RLS policies protect only direct PostgREST/authenticated clients. A compromised API process = full DB.
- Files: `backend/src/backend/composition/live.py`, `supabase-integration/src/supabase_integration/*.py`, `supabase-integration/migrations/001_initial_schema.sql`
- Current mitigation: Secrets only in server env (never `VITE_`); JWT + corporate email gate on HTTP deps; admin gated via `profiles.role` not JWT claim (`deps.require_admin`).
- Recommendations: Minimize service_role surface; prefer SECURITY DEFINER RPCs with explicit checks; never expose secret key to browser.

**RLS policy coverage still incomplete for product tables:**
- Risk: Policies cover ready materials/chunks, digests, own votes, own profile SELECT. Authenticated clients lack SELECT on `topics`, `voting_cycles`, `razbors`, `material_tags`, shortlist, etc.
- Files: `supabase-integration/migrations/001_initial_schema.sql` (RLS ~240–297), `supabase-integration/README.md`
- Current mitigation: Default-deny for anon; app reads go through FastAPI + service_role.
- Recommendations: If browser ever talks PostgREST directly, add least-privilege policies first; keep privileged writes server-side.

**`votes_update_own` policy alone does not check cycle open:**
- Risk: RLS UPDATE allows own row without `voting_cycles.status = 'open'`.
- Files: `supabase-integration/migrations/001_initial_schema.sql`, `supabase-integration/migrations/003_phase3_voting_ballot.sql` (`enforce_votes_open_cycle_and_topic`)
- Current mitigation: DB trigger enforces open cycle + topic∈cycle; use-case `cast_vote` also checks cycle status.
- Recommendations: Keep trigger + use-case; do not rely on RLS alone if user JWT ever writes votes.

**SPA session in Supabase localStorage (accepted XSS→token theft):**
- Risk: Default supabase-js persistence stores access tokens in browser storage; XSS can exfiltrate.
- Files: `web/src/services/supabaseClient.js`, `web/src/services/authApi.js`, `.planning/milestones/v1-phases/01-platform-foundation-auth/01-SECURITY.md` (AR-01-09)
- Current mitigation: Accepted risk for Phase 1; domain gate; sanitize `returnUrl` (`authEnv.sanitizeReturnUrl`).
- Recommendations: httpOnly BFF session when threat model tightens; strict CSP; never put secret key in Vite.

**Self-hosted Supabase attack surface:**
- Risk: Team owns hardening/backups for `knowledge-db.ru`; open Studio or leaked service_role is catastrophic.
- Files: `docs/adr/0004-self-hosted-supabase-on-vm.md`, `docs/agents/local-platform-runbook.md`
- Current mitigation: Architectural intent to encapsulate access in `supabase-integration` + backend composition.
- Recommendations: Network-restrict Studio/API; rotate keys; policy/RPC regression tests.

**Notebook path containment depends on NOTEBOOK_ROOT config:**
- Risk: Mis-set `NOTEBOOK_ROOT` to overly broad filesystem expands readable files for authenticated users who know relative paths (after resolve checks).
- Files: `backend/src/backend/infrastructure/local_notebook_storage.py`, `backend/src/backend/composition/settings.py`
- Current mitigation: Rejects absolute paths and `..` parts; resolves under root.
- Recommendations: Keep root to a dedicated notebooks tree; prefer object storage later.

## Performance Bottlenecks

**Knowledge hybrid SQL without ANN shortlist:**
- Problem: Full-chunk hybrid scoring in `search_knowledge_chunks` (see Known Bugs).
- Files: `supabase-integration/migrations/004_phase4_knowledge_razbory.sql`
- Cause: Correctness-first Phase 4 RPC over seed data.
- Improvement path: HNSW/IVF candidate retrieval then re-rank with FTS blend; tune `result_limit`.

**Ballot snapshot rebuild after every vote:**
- Problem: `cast_vote` always re-fetches full ballot (topics + counts + personal) after upsert.
- Files: `backend/src/backend/application/use_cases/cast_vote.py`, `get_ballot.py`
- Cause: D-52 honesty snapshot contract.
- Improvement path: Acceptable at current scale; cache tallies or return upsert DTO if load grows.

**Client mock delays add artificial latency:**
- Problem: Mock voting/knowledge paths use `delay()` for UX demos.
- Files: `web/src/utils/delay.js`, `web/src/services/votingApi.js`, `web/src/services/knowledgeApi.js`
- Cause: Prototype honesty harness.
- Improvement path: No-op delay in CI; keep only for local demos.

## Fragile Areas

**Schema / migration contract tests are substring presence checks:**
- Files: `tests/unit/test_schema_migration_contract.py`, `tests/unit/test_phase5_migration_005.py`
- Why fragile: Renames, broken policies, or missing indexes can still “pass”; no live DB apply in CI.
- Safe modification: Change migration then update assertions; add integration migrate+query job before trusting prod.
- Test coverage: Unit contract + offline adapter stubs; no RLS matrix against live DB.

**Embedding dimension + stub algorithm locked across layers:**
- Files: `data-collection/src/data_collection/dto/foundry.py` (`EMBEDDING_DIM = 1024`), migration `vector(1024)`, `StubQueryEmbedder`, seed SQL comments
- Why fragile: Model or dim change requires coordinated migration + reindex + seed rewrite.
- Safe modification: Confirm production embedder before writing real vectors; plan alter+reembed runbook.
- Test coverage: DTO length validator; stub determinism in knowledge tests.

**`design-frontend/scripts/app.js` monolith:**
- Files: `design-frontend/scripts/app.js`
- Why fragile: Large imperative script; easy regressions when syncing UX to React.
- Safe modification: Prefer implementing behavior in `web/`; treat static JS as reference.
- Test coverage: Playwright `tests/design-frontend.spec.js` (separate project).

**Mock harness window flags are sticky global state:**
- Files: `web/src/services/votingApi.js`, `knowledgeApi.js`, `meApi.js`, `authApi.js`
- Why fragile: Playwright/reloads depend on `window.__DIGEST_*__`; leakage between tests if reset missed.
- Safe modification: Always call reset helpers in `beforeEach`; avoid production builds reading harness flags.
- Test coverage: Spec files arm/clear harnesses; fragile if new flags added without cleanup.

**Shared VM migration discipline:**
- Files: `docs/agents/local-platform-runbook.md`
- Why fragile: Human “apply once” stamps; MCP `raw_sql` needs `POSTGRES_URL` many operators lack.
- Safe modification: Record applied date/method in runbook after each file; never wipe.
- Test coverage: None automated against VM.

## Scaling Limits

**Knowledge retrieval:**
- Current capacity: Seed-sized chunk sets + stub embeddings.
- Limit: Full hybrid scan + stub vectors break usefulness and latency as chunk count grows.
- Scaling path: Real embedder + ANN prefilter; optional partition by material status.

**Voting tallies:**
- Current capacity: Fine for homework topic counts.
- Limit: Python aggregation over all topic_materials/votes rows.
- Scaling path: Aggregate SQL; materialized tallies if needed.

**Activity / leaderboard:**
- Current capacity: `activity_events` + platform ping writers exist; public leaderboard deferred (ADR-0001).
- Limit: Unbounded inserts without retention once instrumentation expands.
- Scaling path: Indexes on `user_id`/`created_at` exist; define retention before UI.

**Admin digest send:**
- Current capacity: Stub mailer + atomic claim RPC (post-006).
- Limit: Real SMTP/batch recipients not implemented; no async worker.
- Scaling path: Queue + SmtpMailer; keep claim+publish atomic.

## Dependencies at Risk

**FoundryModels / DeepSeek (Cloud.ru contour):**
- Risk: External ML pipeline for transcript/summary/tags/embeddings (ADR-0002); v1.1 temporarily bends toward DeepSeek captions MVP — no client code in-repo yet.
- Impact: Ingestion and real semantic search blocked; NFR-A3 degradation path unimplemented.
- Migration plan: Stable ports; swap provider adapter without touching domain.

**Self-hosted Supabase + pgvector:**
- Risk: Single shared VM; operator-applied migrations; SDK pinned only in `supabase-integration`.
- Impact: Outage or schema drift blocks all live proof.
- Migration plan: Keep adapters in one package; document backup/rotate; avoid managed-cloud divergence (ADR-0004).

**No CI pipeline:**
- Risk: No `.github/workflows` detected; quality depends on local `npm test` / `uv run pytest`.
- Impact: Broken main can land unnoticed; Playwright browsers via postinstall only.
- Migration plan: Add CI for unit + Playwright web project; optional live smoke as manual/gated job.

**Supabase Auth email confirmation / signup mail deferred:**
- Risk: Self-service signup UX depends on Auth dashboard config; signup mail out of milestone scope.
- Impact: Live registration friction / incomplete onboarding.
- Migration plan: Document Studio Auth settings in runbook; defer product mail.

## Missing Critical Features

**Content ingestion spine (v1.1):**
- Problem: No YouTube→captions→LLM→draft materials CLI; admin UI expects drafts from pipeline/seed.
- Blocks: Fresh weekly content without manual SQL/seed; PIPE-01 honesty vs demo seed (D-78).

**Production embeddings + SMTP:**
- Problem: Stub embedder + StubMailer in live container.
- Blocks: Real semantic search and email delivery NFRs.

**Local/prod parity tooling:**
- Problem: No app Dockerfile/Compose; migrate-by-operator only.
- Blocks: Repeatable onboarding without shared VM access.

**httpOnly session / BFF:**
- Problem: Deferred past Phase 1 security acceptance.
- Blocks: Stronger XSS resistance for corporate deployment.

## Test Coverage Gaps

**No live Supabase / RLS integration suite in CI:**
- What's not tested: Real PostgREST+RLS deny/allow, migration apply on ephemeral DB, Foundry/YouTube HTTP, end-to-end live FE↔BE under `VITE_USE_MOCKS=false`.
- Files: `tests/unit/test_supabase_*_contract.py` (offline stubs), `tests/*.spec.js` (mostly mocks)
- Risk: Green unit suite with broken production path or unapplied 006.
- Priority: High before claiming production readiness

**Ingestion / ranking pipeline untested (absent):**
- What's not tested: YouTube captions, LLM draft write, shortlist enqueue, PIPE-01 scores.
- Files: Planned under `.planning/` Phase 6+; `data-collection` DTO unit tests only
- Risk: First real pipeline lands without regression net.
- Priority: High for v1.1

**Auth domain restriction covered in unit; live Auth edge cases thin:**
- What's tested: `is_allowed_corporate_email`, JWT verify unit, Playwright auth under mocks.
- What's thin: Live signup confirmation, lockout, JWKS rotation failures.
- Files: `tests/unit/test_auth_email_domain.py`, `tests/unit/test_jwt_verify.py`, `tests/auth.spec.js`
- Priority: Medium (raise when live Auth is default)

**Performance / load:**
- What's not tested: Hybrid search latency at corpus scale; concurrent vote CAS; admin send under contention.
- Priority: Medium (post-seed)

---

*Concerns analysis: 2026-09-26*
