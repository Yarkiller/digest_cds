# Digest CDS

## What This Is

Digest CDS is an editorial knowledge service for СВА (Служба внутреннего аудита) Сбербанка. It turns external video/text into agent-prepared articles, then delivers weekly digests, topic voting → разборы, and semantic knowledge search for рядовой сотрудник СВА, Data Analyst, Data Scientist, and Админ (CDS/делегат).

## Core Value

Authorized СВА staff can read a trustworthy weekly issue of prepared articles and influence the next разбор through one honest vote — without treating raw video/transcript as published material.

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

<!-- Inferred from brownfield map `.planning/codebase/` — scaffolding that already exists. -->

- ✓ Ports & Adapters layout (`backend/`, `supabase-integration/`, `data-collection/`, `web/`) — brownfield
- ✓ Initial Supabase schema + RLS SQL (`supabase-integration/migrations/001_initial_schema.sql`) — brownfield
- ✓ React/Vite Editorial UI shell with mock data (`web/`) + design canon (`design-frontend/`) — brownfield
- ✓ Domain entities/ports for Material & Knowledge (in-memory composition) — brownfield
- ✓ Playwright E2E harness + pytest unit layout — brownfield

### Validated

- ✓ Corporate auth + session redirect (AUTH-*) — Phase 1
- ✓ Current issue, materials (prepared article only), archive (ISSUE-*, MAT-*) — Phase 2
- ✓ Voting cycle: one vote, change while open, audit-language ballot (VOTE-*) — Phase 3

### Active

<!-- Current v1 scope — see REQUIREMENTS.md for IDs and acceptance. -->

- [ ] Knowledge semantic search + role filters; разборы list/longread/notebook (KNOW-*, RAZB-*)
- [ ] Admin shortlist → approve/reject → preview → send → archive (ADMIN-*)
- [ ] Platform: live DB, FastAPI, FE↔BE, security, errors, docs (PLAT-*)

### Out of Scope

- Public leaderboard / gamification UI — deferred past v1 (ADR-0001 locked); activity events may be collected
- Quiz cards (карточки с вопросами) — post-v1 (REQ-US-29)
- Admin YAML pipeline config UI — post-v1 (REQ-US-30)
- XP, streaks, anonymous average comparison — rejected / not v1
- Storing or publishing video/audio/raw transcript as material — content contract
- Public foreign LLM/Whisper APIs; local Whisper on app VM — ADR-0002
- Managed Supabase Cloud / managed PostgreSQL Cloud.ru as primary DB — ADR-0004
- Dynamic admin-managed email domain list — ADR-0003 (fixed two domains only)

## Context

- **Product framing:** Concept 3 Editorial UI («Digest CDS: издание»); personas and journeys J1–J6 in ingest context.
- **Brownfield:** Frontend mostly mock-backed; FastAPI HTTP layer and live Supabase adapters not wired yet; schema/RLS migration exists.
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
*Last updated: 2026-09-20 after Phase 3*
