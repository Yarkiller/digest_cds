# Digest CDS

## What This Is

Digest CDS is an editorial knowledge service for СВА (Служба внутреннего аудита) Сбербанка. It turns external video/text into agent-prepared articles, then delivers weekly digests, topic voting → разборы, and semantic knowledge search for рядовой сотрудник СВА, Data Analyst, Data Scientist, and Админ (CDS/делегат).

## Core Value

Authorized СВА staff can read a trustworthy weekly issue of prepared articles and influence the next разбор through one honest vote — without treating raw video/transcript as published material.

## Current State

v1 MVP shipped 2026-09-22. Five phases are verified: corporate auth on live Supabase, the current issue and archive, one honest vote, knowledge search and разборы, and admin shortlist → preview → send. Outbound mail stays on StubMailer. Signup confirmation mail on the shared VM is still unresolved (`g-01-3b-signup-mailer`).

About 11,100 lines of Python and 8,400 lines of JS/JSX. Stack: FastAPI, React/Vite, self-hosted Supabase + pgvector, Playwright, pytest. Git range `cabd7eb` → `ba8be89` (330 commits, 2026-08-23 → 2026-09-22).

## Current Milestone: v1.1 YouTube → LLM → Supabase ingestion

**Goal:** Operator can run a CLI one-shot that turns a YouTube URL into a `materials` draft and a shortlist row — without touching backend/SPA read paths.

**Target features:**
- Expand `data-collection/` ports/DTOs: Transcript, VideoMetadata, MaterialDraft, TemplateKind
- New thin `ingestion-service/` CLI runner (no HTTP API, no scheduler)
- YouTube captions via `youtube-transcript-api` (no Whisper / FoundryModels transcription)
- DeepSeek via OpenAI-compatible SDK — MVP LLM; FoundryModels revisit later
- 1–2 prompt templates (`lecture.md`, `podcast.md`)
- Pipeline: URL → transcript → LLM → markdown → Supabase `materials` (`status=draft`) + enqueue `digest_shortlist_items`
- UAT: 3–5 real videos appear as drafts in `/admin/digest`

**Deferred from this milestone (still post-v1):** Public leaderboard, quiz cards, admin YAML pipeline UI, live SMTP, signup confirmation mail.

## Success Criteria (v1 — developer-facing)

v1 is done only when **all** of the following hold:

1. **Backend operability** — DB deployed and working; API endpoints correct; no critical errors.
2. **Frontend–Backend integration** — Frontend connects to Backend; data loads from server; data posts to server; app works end-to-end.
3. **Security** — authentication configured; access policies (RLS or middleware); secrets not in code; CORS correct.
4. **Error handling** — network errors handled; validation errors handled; errors logged.
5. **Delivery quality** — code structured and readable; documentation complete and clear; deployment instructions work; process documented.

**Target runtime:** Cursor (solo developer + Claude workflow).

## Requirements

### Validated

- ✓ Ports & Adapters layout (`backend/`, `supabase-integration/`, `data-collection/`, `web/`) — brownfield
- ✓ Initial Supabase schema + RLS SQL (`supabase-integration/migrations/001_initial_schema.sql`) — brownfield
- ✓ React/Vite Editorial UI shell with mock data (`web/`) + design canon (`design-frontend/`) — brownfield
- ✓ Domain entities/ports for Material & Knowledge (in-memory composition) — brownfield
- ✓ Playwright E2E harness + pytest unit layout — brownfield
- ✓ Platform: live DB, FastAPI, FE↔BE, security, errors, docs (PLAT-*) — v1
- ✓ Corporate auth + session redirect (AUTH-*) — v1
- ✓ Current issue, materials (prepared article only), archive (ISSUE-*, MAT-*) — v1
- ✓ Voting cycle: one vote, change while open, audit-language ballot (VOTE-*) — v1
- ✓ Knowledge semantic search + role filters; разборы list/longread/notebook (KNOW-*, RAZB-*) — v1
- ✓ Admin shortlist → approve/reject → preview → send → archive (ADMIN-*) — v1
- ✓ `data-collection` ports/DTOs: Transcript, VideoMetadata, MaterialDraft, TemplateKind + TranscriptProvider/ArticleGenerator fakes (DTO-01, DTO-02) — Phase 6
- ✓ YouTube URL → `video_id` + captions (`ru`/`en`) via injected `youtube-transcript-api`; fail-closed `stage=captions` at unit/adapter level (CAP-01, CAP-02) — Phase 7
- ✓ `VideoMetadataProvider` + oEmbed + `ingestion-service` Settings/proxy composition (no Typer yet) — Phase 7
- ✓ DeepSeek article generation via lecture/podcast templates with fail-closed LLM errors, budget check, and redacted diagnostics (LLM-01…LLM-05) — Phase 8

### Active

- [ ] `ingestion-service` CLI one-shot: YouTube URL → captions → DeepSeek → materials draft + shortlist enqueue
- [ ] UAT: 3–5 real videos visible as drafts in `/admin/digest`

### Out of Scope

- XP, streaks, anonymous average comparison — rejected for v1 and still rejected as the participation driver
- Storing or publishing video/audio/raw transcript as material — content contract
- Whisper / FoundryModels transcription this milestone — captions-only; FoundryModels revisit after DeepSeek MVP
- Ingestion HTTP API, scheduler/batch, auto-publish/send — later milestones
- Public leaderboard, quiz cards, admin YAML pipeline UI, live SMTP, signup mail — deferred (not this milestone)
- Managed Supabase Cloud / managed PostgreSQL Cloud.ru as primary DB — ADR-0004
- Dynamic admin-managed email domain list — ADR-0003 (fixed two domains only)

## Context

- **Shipped v1:** Auth, issue/materials/archive, voting, knowledge search, разборы, and admin digest publish. Live adapters through migration 005. Mail is StubMailer.
- **v1.1 focus:** Separate ingestion path (`data-collection` contracts + `ingestion-service` CLI) writes drafts into the same Supabase DB; backend/SPA unchanged as readers. DeepSeek MVP bends ADR-0002 temporarily (documented revisit → FoundryModels).
- **Product framing:** Concept 3 Editorial UI («Digest CDS: издание»); personas and journeys J1–J6 in ingest context.
- **Known debt at close:** Nyquist drafts for phases 1–3; live FE↔BE smoke still human-gated under mocks in CI; rank rewrite before `claim_and_publish_digest` is non-atomic (CR-01); four debug sessions acknowledged 2026-09-22 (see STATE.md Deferred Items).
- **Domain language:** `CONTEXT.md` + `docs/adr/` are canonical for agents.
- **Intel source:** `.planning/intel/` (ingest MODE=new, READY, 0 blockers).
- **Preserve:** `.planning/codebase/` brownfield map — do not delete.

## Constraints

- **Protocol / TDD**: Red–Green–Refactor mandatory; no production code without a failing test first.
- **Architecture**: Ports & Adapters; domain/use-cases free of FastAPI/httpx/supabase; wiring only in `composition/`.
- **Content contract**: Material = agent-prepared article only; video/audio are transient pipeline input.
- **Stack**: App on Cloud.ru VM; FoundryModels for ML pipeline; self-hosted Supabase+pgvector on separate VM (Docker Compose); `web/` Vite+React+Tailwind; Playwright UI tests; Python via `uv`.
- **Security**: Email domains `@sberbank.ru` / `@omega.sbrf.ru` only; secrets in env/Cloud.ru only; NFR-S* and error-handling contracts apply.
- **NFR**: Issue/material/search/admin p95 targets; read-path availability; FoundryModels async and non-blocking for published content.
- **Error UX**: Inline field errors, editorial empty states, banners/toasts with Retry, 401→login?returnUrl=, Russian copy per CONTEXT.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Public leaderboard deferred past v1 (ADR-0001) | Collect activity in v1; show leaderboard later | ✓ Locked |
| Cloud.ru VM + FoundryModels pipeline (ADR-0002) | Contour isolation; no public foreign LLM/Whisper | — Pending (proposed) |
| Fixed email domains only (ADR-0003) | Corporate access without dynamic whitelist UI | — Pending (proposed) |
| Self-hosted Supabase on separate VM (ADR-0004) | Own Postgres+pgvector+Auth; reject managed Cloud | — Pending (proposed) |
| Material = prepared article only | Editorial trust; no media-as-material | ✓ Locked (SPEC/content) |
| Ports & Adapters + TDD | Architecture & AGENTS rules | ✓ Locked |
| Announcement разборы suppress read CTA (G-04-2) | Visual honesty: unpublished status must not look readable | ✓ Phase 4 |
| Admin send publishes an issue and claims sent_at before stub mail (D-88, D-87) | Archive and the email link must match a real issue; SMTP is not live yet | ✓ Phase 5 |
| Self-service `/register` with Логин; login is email+password (G-01-3) | UAT showed a dead registration CTA and a name field on login | ✓ Phase 1 |
| Typography-only issue hero (D-26) | Current issue shows number, period, and title | ✓ Phase 2 |
| StubMailer until SMTP is configured | Publish and the issue link must exist before live mail | ✓ Phase 5 |
| Four debug sessions acknowledged at v1 close | Diagnosis files stayed open after the gap-closure plans; signup mailer is still unknown | — Deferred |
| DeepSeek MVP for ingestion LLM (ADR-0002 bend) | Captions-only pipeline first; one external LLM; FoundryModels revisit later | — Pending |
| Ingestion writes Supabase only; no backend coupling | Backend/SPA stay readers; CLI owns YouTube + LLM + shortlist enqueue | — Pending |
| Phase 6 six-name public `__all__`; brownfield YouTube/Foundry/text-import DTOs deleted (D-01…D-03) | Single ingestion contract; no parallel public DTO names | ✓ Phase 6 |
| Captions list-then-pick + CaptionsError→locked reasons; CAP-02 live persist spy deferred (D-14) | Adapter-boundary SDK mapping; zero-row proof at unit level until Phase 9/10 | ✓ Phase 7 |
| Phase 7 seven-name public `__all__` (+ VideoMetadataProvider); proxy only in composition | Adapters take ready clients; no `os.environ` in adapters (D-17) | ✓ Phase 7 |
| DeepSeek via OpenAI-compatible SDK with injected client, `response_format=json_object`, disabled thinking, and composition-only env | No `os.environ` in adapters; caller controls client and secrets (D-07, D-11, D-14) | ✓ Phase 8 |
| `ArticleDraft` validation + `ArticleError` taxonomy; redacted diagnostics and locked `LLM_REASONS` | Provenance label caller-supplied; no transcript/key in operator JSON (D-12, D-13) | ✓ Phase 8 |
| Character cap enforced before DeepSeek call; `ArticleBudgetError` maps to `stage=llm_truncation` | No silent truncation; context limited to `char_count`/`max_chars` (D-08, D-09, D-10) | ✓ Phase 8 |
| Public `data_collection.__all__` stays seven names; new symbols negative-rooted | Adapter/error/template loader are module-private; `Stage` set unchanged (D-04, D-06) | ✓ Phase 8 |

<decisions>
## Locked decisions (from ADRs / ingest)

### ADR-0001 — Public leaderboard (LOCKED)
- **D-ADR-0001:** Do not ship a public leaderboard or gamification UI in v1. Activity may be collected from digests, voting, and related events; the public leaderboard is deferred past v1. Rejected for long-term design: private-only stats and anonymous average comparison as the primary participation driver.
  — **Reversibility:** costly — shipping a public ranking UI later requires product/IA work and may re-open privacy expectations already set with СВА users.
  — **Source:** `docs/adr/0001-public-leaderboard-gamification.md`

### ADR-0002 — Cloud.ru + FoundryModels (proposed → project constraint)
- **D-ADR-0002:** Deploy Digest CDS on a Cloud.ru VM. Process YouTube/text via FoundryModels API (transcription/import, summarization, analysis, tagging, embeddings) — not public foreign APIs and not local Whisper on the app VM. Store prepared article + provenance metadata; do not store media as material.
  — **Reversibility:** costly — provider change requires ML-pipeline adapter swap and redeploy.
  — **Source:** `docs/adr/0002-cloud-ru-foundrymodels-deployment.md`

### ADR-0003 — Email domain restriction (proposed → project constraint)
- **D-ADR-0003:** Registration/login limited to fixed domains `@sberbank.ru` and `@omega.sbrf.ru` via config; no dynamic admin-managed domain list in v1.
  — **Reversibility:** reversible — domain list is config-driven; adding domains is cheap, changing the “no admin UI” policy is a product decision.
  — **Source:** `docs/adr/0003-email-domain-restriction.md`

### ADR-0004 — Self-hosted Supabase (proposed → project constraint)
- **D-ADR-0004:** Use self-hosted Supabase (PostgreSQL + pgvector, Auth/Storage/REST) on a separate VM via Docker Compose; reject managed Supabase Cloud and managed PostgreSQL Cloud.ru as primary. Access encapsulated in `supabase-integration`; initial schema/RLS in `001_initial_schema.sql`.
  — **Reversibility:** one-way — operational ownership of backups/HA and migration path away from self-hosted is a platform commitment.
  — **Source:** `docs/adr/0004-self-hosted-supabase-on-vm.md`

### Content & process (SPEC / AGENTS)
- **D-CONTENT-01:** Published material is only an agent-prepared article; raw transcript/video/audio are never material content.
- **D-PROC-01:** TDD Red–Green–Refactor is mandatory for behavior changes.
- **D-ARCH-01:** Hexagonal Ports & Adapters; adapters in `supabase-integration` / `data-collection`; composition root owns wiring.

### Claude's Discretion
- Exact FastAPI route layout and FE service module split within Ports & Adapters and `web/src/services/`.
- FoundryModels client internals inside `data-collection` as long as DTOs/ports stay clean.
</decisions>

## Evolution

After each phase transition: move validated/invalidated requirements; log decisions; keep “What This Is” accurate.
After milestone: full review of Core Value, Out of Scope, and Context against shipped reality.

---
*Last updated: 2026-09-27 after Phase 8*
