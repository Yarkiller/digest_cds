---
gsd_state_version: 1.0
current_phase: 02
current_phase_name: Issue, Materials & Archive
status: executing
stopped_at: Completed 02-04-PLAN.md
last_updated: "2026-09-20T10:51:11.516Z"
last_activity: 2026-09-20
last_activity_desc: Phase 02 execution started
state_head: dae418554979812eca4a7d4cd31525eb59b15662
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 15
  completed_plans: 12
  percent: 20
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-19)

**Core value:** Trusted weekly prepared-article issue + one honest vote toward the next разбор
**Current focus:** Phase 02 — Issue, Materials & Archive

## Current Position

Phase: 02 (Issue, Materials & Archive) — EXECUTING
Plan: 5 of 6
Status: Ready to execute
Last activity: 2026-09-20 — Phase 02 execution started

Progress: [██░░░░░░░░] 20%

## Performance Metrics

**Velocity:**

- Total plans completed: 6
- Average duration: ~7min (plans 01–05 timed)
- Total execution time: ~35min + 01-06 docs/human follow-up

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Platform Foundation & Auth | 6 | 6 executed | ~7min |

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

### Pending Todos

None — ready to plan/execute Phase 2.

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

Last session: 2026-09-20T10:51:11.351Z
Stopped at: Completed 02-04-PLAN.md
Resume file: None
Verification: `.planning/phases/01-platform-foundation-auth/01-VERIFICATION.md`
