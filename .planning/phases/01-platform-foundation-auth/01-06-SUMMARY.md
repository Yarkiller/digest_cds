---
phase: 01-platform-foundation-auth
plan: 06
subsystem: infra
tags: [docs, runbook, cloudru, plat-08, live-proof, d-05, d-07, d-08, d-10]

requires:
  - phase: 01-platform-foundation-auth
    provides: Live Supabase adapters (01-04); SPA Auth + meApi (01-05); FastAPI /me + /me/ping
provides:
  - docs/agents/local-platform-runbook.md (local Vite+API against remote Supabase + Auth seed + live checklist)
  - docs/agents/cloudru-app-deploy-path.md (future app VM path; Phase 1 does not deploy)
  - README links + npm run platform:runbook helper
affects:
  - Phase 1 verification / human UAT for ROADMAP success criteria 3–5
  - Later Cloud.ru app deploy plans

actuals:
  tokens: 3200
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - PLAT-08 docs split: local runbook vs Cloud.ru path-only
    - Auth seed steps live in runbook (D-08), not automated against shared VM

key-files:
  created:
    - docs/agents/local-platform-runbook.md
    - docs/agents/cloudru-app-deploy-path.md
  modified:
    - README.md
    - package.json

key-decisions:
  - "Auth dashboard seed steps (1–2 corporate users) documented in runbook §4, deferred from 01-04"
  - "npm platform:runbook prints paths/commands only — no secret-bearing scripts"
  - "Live FE↔BE proof left to blocking-human checkpoint — not fabricated"

patterns-established:
  - "Operator live proof checklist in docs/agents; CI not gated on live credentials (RESOLVED RESEARCH Q3)"

requirements-completed: [PLAT-08]

coverage:
  - id: D1
    description: "Local platform runbook covers env, uv/uvicorn, Vite, Auth seed, live checklist"
    requirement: PLAT-08
    verification:
      - kind: other
        ref: "Test-Path docs/agents/local-platform-runbook.md; README link local-platform-runbook"
        status: pass
    human_judgment: false
  - id: D2
    description: "Cloud.ru deploy-path doc states Phase 1 does not deploy; linked from README"
    requirement: PLAT-08
    verification:
      - kind: other
        ref: "docs/agents/cloudru-app-deploy-path.md#Phase 1 does not deploy"
        status: pass
    human_judgment: false
  - id: D3
    description: "Live FE↔BE proof: corporate login → GET /me → POST /me/ping → activity_events"
    requirement: PLAT-03
    verification: []
    human_judgment: true
    rationale: "Blocking-human checkpoint; executor must not fabricate live-proof success. Operator .env incomplete for full live (missing JWT issuer, CORS, APP_CONTAINER, VITE_*)."

duration: 8min
completed: 2026-09-19
status: halted
---

# Phase 01 Plan 06: Local/Cloud.ru Docs + Live Proof Summary

**PLAT-08 runbooks shipped (local bring-up + Cloud.ru path-only); live FE↔BE proof is AWAITING human approval — not claimed green.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-09-19T15:33:24Z
- **Completed:** 2026-09-19 (docs tasks); live proof pending
- **Tasks:** 2/3 auto complete; Task 3 checkpoint open
- **Files modified:** 4

## Accomplishments

- `docs/agents/local-platform-runbook.md` — D-05 local Vite+API vs remote Supabase; D-08 Auth seed; D-10 checklist; PLAT-01 no local Docker Supabase; RESOLVED RESEARCH Q3 note
- `docs/agents/cloudru-app-deploy-path.md` — future app VM outline; **Phase 1 does not deploy** (D-07)
- README links both docs; `npm run platform:runbook` prints safe commands only

## Task Commits

1. **Task 1: Write local platform runbook** — `3b91b10` — `docs(01-06): add local platform runbook and README link`
2. **Task 2: Document Cloud.ru app deploy path only** — `5818056` — `docs(01-06): document Cloud.ru app deploy path without deploying`
3. **Task 3: Live FE↔BE platform proof** — **AWAITING** human approval (`checkpoint:human-verify`, `gate=blocking-human`)

## Files Created/Modified

- `docs/agents/local-platform-runbook.md` — full local + live-proof operator guide
- `docs/agents/cloudru-app-deploy-path.md` — deploy path docs only
- `README.md` — links + shortened Local platform section pointing at runbooks
- `package.json` — `platform:runbook` helper

## Decisions Made

- Seed steps for 1–2 `@sberbank.ru` / `@omega.sbrf.ru` users live in runbook §4 (from deferred 01-04)
- Did not start a fabricated live-proof session: root `.env` has remote Supabase URL/keys/JWKS but is missing `SUPABASE_JWT_ISSUER`, `API_CORS_ORIGINS`, `APP_CONTAINER`, and all `VITE_*` live-proof vars

## Deviations from Plan

None - plan executed exactly as written for Tasks 1–2. Task 3 correctly halted for human verification.

## Issues Encountered

- Operator `.env` incomplete for automated live assist — documented in checkpoint; human must finish env + Auth seed + checklist

## User Setup Required

| Item | Status | Needed for |
|------|--------|------------|
| Fill missing `.env` (JWT issuer, CORS, `APP_CONTAINER=live`, `VITE_*`, `VITE_USE_MOCKS=false`) | Pending | Live proof |
| Create 1–2 Auth users on knowledge-db.ru dashboard | Pending (D-08) | Login step |
| Run checklist in runbook §5; type **approved** | Pending | Close Phase 1 observable criteria 3–5 |

## Next Phase Readiness

Docs ready. Phase 1 ROADMAP success criteria 3–5 **not** observably closed until human types `approved` after live proof. Do not treat plan as fully complete until then.

## Known Stubs

None in docs deliverables. Live proof itself is intentionally unproven.

## Threat Flags

None beyond plan model — docs warn against pasting secrets and forbid destructive VM SQL during proof (T-01-13, T-01-14).

## Self-Check: PASSED

- FOUND: docs/agents/local-platform-runbook.md
- FOUND: docs/agents/cloudru-app-deploy-path.md
- FOUND: README.md links for both
- FOUND: 3b91b10, 5818056
- Live proof: AWAITING (not claimed)

---
*Phase: 01-platform-foundation-auth*
*Completed: 2026-09-19 (docs); live proof pending*
