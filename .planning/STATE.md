---
gsd_state_version: 1.0
current_phase: 04
current_phase_name: Knowledge & Razbory
status: verifying
stopped_at: Completed 04-09-PLAN.md
last_updated: "2026-09-21T09:26:22.257Z"
last_activity: 2026-09-21
last_activity_desc: Phase 04 execution started
state_head: fde14e49381e475e2b300a37720cb915d11edd72
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 30
  completed_plans: 29
  percent: 60
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-20)

**Core value:** Trusted weekly prepared-article issue + one honest vote toward the next разбор
**Current focus:** Phase 04 — Knowledge & Razbory

## Current Position

Phase: 04 (Knowledge & Razbory) — EXECUTING
Plan: 9 of 9
Status: Phase complete — ready for verification
Last activity: 2026-09-21 — Phase 04 execution started

Progress: [███████████████████░] 20/21 plans ([██████░░░░] 60%)

## Performance Metrics

**Velocity:**

- Total plans completed: 18
- Average duration: ~7min (plans 01–05 timed)
- Total execution time: ~35min + 01-06 docs/human follow-up

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Platform Foundation & Auth | 6 | 6 executed | ~7min |
| 02 | 6 | - | - |
| 03 | 6 | - | - |

**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | 4min | 3 tasks | 16 files |
| Phase 01 P02 | 12min | 2 tasks | 16 files |
| Phase 01 P03 | 3min | 2 tasks | 9 files |
| Phase 01 P04 | 4min | 3 tasks | 15 files |
| Phase 01 P05 | 12min | 3 tasks | 16 files |
| Phase 01 P06 | follow-up | 3 tasks | docs + human proof |
| Phase 02 P01 | 10min | 3 tasks | 18 files |
| Phase 02 P02 | 45min | 3 tasks | 11 files |
| Phase 02 P03 | 7min | 2 tasks | 15 files |
| Phase 02 P04 | 17min | 3 tasks | 14 files |
| Phase 02 P05 | 7min | 2 tasks | 16 files |
| Phase 02 P05 | 7min | 2 tasks | 16 files |
| Phase 02 P06 | 12min | 2 tasks | 9 files |
| Phase 03 P01 | 22min | 2 tasks | 13 files |
| Phase 03-voting-cycle P03 | 4min | 2 tasks | 1 files |
| Phase 03-voting-cycle P05 | 8min | 2 tasks | 6 files |
| Phase 03-voting-cycle P02 | 45min | 3 tasks | 7 files |
| Phase 03-voting-cycle P06 | 8min | 2 tasks | 9 files |
| Phase 03 P04 | 12min | 3 tasks | 8 files |
| Phase 04 P01 | 7min | 2 tasks | 11 files |
| Phase 04-knowledge-razbory P02 | 5min | 2 tasks | 5 files |
| Phase 04-knowledge-razbory P04 | 3min | 2 tasks | 13 files |
| Phase 04-knowledge-razbory P03 | 15min | 2 tasks | 9 files |
| Phase 04 P05 | 5min | 2 tasks | 7 files |
| Phase 04-knowledge-razbory P06 | 5min | 2 tasks | 8 files |
| Phase 04-knowledge-razbory P07 | 12min | 2 tasks | 14 files |
| Phase 04-knowledge-razbory P08 | continuation-closeout | 3 tasks | 9 files |
| Phase 04-knowledge-razbory P09 | 9min | 2 tasks | 9 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions and `<decisions>` blocks.

- ADR-0001 locked: public leaderboard deferred past v1
- ADR-0002…0004 adopted as project constraints (proposed ADRs)
- Brownfield `.planning/codebase/` preserved
- [Phase 1]: Pin RESEARCH FastAPI stack versions after human package approval
- [Phase 1]: create_app(settings) injectable; HTTP edge only under interface/http
- [Phase 1]: Exact corporate email domain match after @ (not endswith) to avoid subdomain spoofing
- [Phase 1]: AccessTokenClaims in domain; JWT verify only in infrastructure; injectable signing_key_resolver for offline tests
- [Phase 1]: PingRecorder returns recorded id; POST /me/ping body {ok,id}; empty payload until Plan 04
- [Phase 1]: AUTH-03 admin-API 403 remains deferred to Phase 5; /me/ping uses JWT+domain gate only
- [Phase 1]: APP_CONTAINER=memory|live selects builder; service_role only in composition/live.py
- [Phase 1]: Auth dashboard user seed deferred to Plan 01-06 live proof (D-08)
- [Phase 1]: Mock authApi/meApi when VITE_USE_MOCKS!==false; live only when false
- [Phase 1]: RequireAuth skips gate when mocks on; force-gate via window.__DIGEST_FORCE_AUTH_GATE__
- [Phase 1]: sanitizeReturnUrl same-origin relative paths only
- [Phase 1]: PLAT-08 local runbook + Cloud.ru path-only docs; live FE↔BE proof human-approved 2026-09-19
- [Phase 1]: Verification PASS_WITH_GAPS — admin 403 → Phase 5; Cloud.ru deploy docs-only; logout UI non-blocking
- [Phase 02]: CurrentIssueResponse uses flat null fields + items=[] for no published issue
- [Phase 02]: Empty Playwright arm uses window.__DIGEST_EMPTY_CURRENT_ISSUE__ across full reloads
- [Phase 02]: live.py wires empty InMemoryIssueRepository until 02-02 Supabase adapter
- [Phase 02]: Seed applied via Supabase MCP PostgREST insert (service_role) because raw_sql needs POSTGRES_URL
- [Phase 02]: voting_cycles idempotency uses WHERE NOT EXISTS on opens_at/closes_at (no unique constraint)
- [Phase 02]: MaterialRepository.get_by_slug + ready-only related filter landed for MAT-01 readiness
- [Phase 02]: GET /archive via sibling archive_router; past issues reuse CurrentIssueResponse without voting_cycle
- [Phase 02]: Issue soft-404 uses ContentApiError NOT_FOUND; EditorialCallout only when IssuePage isCurrent
- [Phase 02]: MaterialNotFoundError accepts int|str for slug misses; draft always 404
- [Phase 02]: Editor byline constant «Редакция Digest CDS» in material reader DTO
- [Phase 02]: MaterialPage uses rehypeSlug+rehypeSanitize only; soft NOT_FOUND via contentApi
- [Phase 02]: Cycle selection in get_current_issue (A2); adapters list_cycles only
- [Phase 02]: SupabaseVotingCycleReader sibling module; past issues force voting_cycle=null
- [Phase 02]: Cycle selection in get_current_issue (A2); adapters list_cycles only
- [Phase 02]: SupabaseVotingCycleReader sibling module; past issues force voting_cycle=null
- [Phase 02]: Sticky __DIGEST_FAIL_NEXT_CONTENT__ for StrictMode; clear on Retry (D-21..23)
- [Phase 02]: UI-SPEC visual backstops describe.skip held for verify-work
- [Phase 03]: D-52: POST /voting/votes returns full BallotSnapshot
- [Phase 03]: live.py keeps InMemoryVoteRepository until 03-02 Supabase adapter
- [Phase 03]: Reuse select_active_voting_cycle; status column is open/closed switch
- [Phase 03]: Leaders/ties/hide-when-zero already in get_ballot from 03-01 — plan 03-03 adds contract tests only
- [Phase 03]: Closed-cycle GET reuses select_active_voting_cycle (latest closed when no open)
- [Phase 03]: Empty «Выберите тему» shown when ready && !selectedId (disabled CTA cannot receive click)
- [Phase 03]: SPA votingApi uses isMocksEnabled; POST BallotSnapshot applied without mandatory re-GET (D-52, D-56)
- [Phase 03]: Option-a: votes_enforce_open_and_topic trigger + use-case (not use-case-only)
- [Phase 03]: 03-02 apply: MCP PostgREST seed + Studio SQL DDL (raw_sql/db push unavailable)
- [Phase 03]: AutoML topic seeded with zero topic_materials (VOTE-04)
- [Phase 03]: Leader strip test uses exact:true for «Лидирует» so strip phrase does not false-fail
- [Phase 03]: Confirm CTA omitted entirely when cycle.status===closed (not merely disabled)
- [Phase 03]: Mock closed POST throws CYCLE_CLOSED with ballot payload for D-51 readiness
- [Phase 03]: 409 detail.ballot for CYCLE_CLOSED/VOTE_CONFLICT; expected_updated_at CAS only (no ETag)
- [Phase 03]: GET ballot fail → ServiceUnavailable; POST fail → ErrorPanel; toast fade ~4s
- [Phase 04]: [Phase 04]: Default knowledge search limit=10 with has_more via limit+1 (D-61)
- [Phase 04]: [Phase 04]: StubQueryEmbedder 1024-d; Foundry HTTP deferred; max q 500 code points
- [Phase 04]: [Phase 04]: Knowledge SPA Submit/Enter via knowledgeApi; blank/overlong client guards (500 code points); role chips deferred to 04-03
- [Phase 04]: [Phase 04]: GET /razbory items[] chronology DTO; announcement|published status strings; empty 200; PersistenceError→503
- [Phase 04]: [Phase 04]: live.py keeps InMemoryRazborRepository until Supabase razbor adapter
- [Phase 04]: Invalid knowledge role is 400 invalid_role; SPA toasts Фильтр недоступен and resets to Все
- [Phase 04]: Null, empty, and whitespace knowledge role means unrestricted (Все)
- [Phase 04]: Zero-hit Сбросить фильтр clears role only and keeps the query (D-65)
- [Phase 04]: [Phase 04]: Razbor list SPA ChronologyItem + byline constant; empty CTA /voting only (D-66…D-69)
- [Phase 04]: [Phase 04]: /razbory/:id shell placeholder until 04-06 detail
- [Phase 04]: [Phase 04]: RazborDetail view carries content_kind; domain Razbor unchanged
- [Phase 04]: [Phase 04]: Announcement prose emptied in get_razbor (D-68 / T-04-10)
- [Phase 04]: [Phase 04]: Notebook strip deferred to 04-07; notebook_available on detail DTO
- [Phase 04]: [Phase 04]: Notebook under NOTEBOOK_ROOT via LocalNotebookStorage; path escape 400 (A5 / T-04-09)
- [Phase 04]: [Phase 04]: Dual notebook strip on published only; announcement omits strip (D-70…72)
- [Phase 04]: Hybrid fusion via SECURITY INVOKER RPC search_knowledge_chunks — not list_all + Python cosine on live
- [Phase 04]: StubQueryEmbedder aligned with seeded 1024-d vectors for demo semantic hits (Foundry opt-out)
- [Phase 04]: Blocking human apply: operator confirmed SQL + notebook + NOTEBOOK_ROOT before 04-08 close-out
- [Phase 04]: [Phase 04]: Playwright honesty suites in knowledge.spec.js/razbory.spec.js; mocks CI default
- [Phase 04]: [Phase 04]: TOC ids use user-content- prefix to match rehype-sanitize clobber

### Pending Todos

None — ready to execute Phase 3 (`/gsd-execute-phase 3`).

### Blockers/Concerns

None. Live FE↔BE proof approved 2026-09-19.

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| Post-v1 | Public leaderboard (ADR-0001) | Deferred | 2026-09-19 | v1 |
| Post-v1 | Quiz cards (REQ-US-29) | Deferred | 2026-09-19 | v1 |
| Post-v1 | Admin YAML pipeline UI (REQ-US-30) | Deferred | 2026-09-19 | v1 |
| Phase 5 | AUTH-03 admin-API 403 | Deferred | 2026-09-19 | Phase 1 verify |
| Ops | Cloud.ru app VM deploy (D-07) | Docs only | 2026-09-19 | Phase 1 |
| UX | Logout button in shell | Non-blocking | 2026-09-19 | Phase 1 |

## Session Continuity

Last session: 2026-09-21T09:26:21.178Z
Stopped at: Completed 04-09-PLAN.md
Resume file: None
Verification: `.planning/phases/01-platform-foundation-auth/01-VERIFICATION.md`
