---
status: testing
phase: 14-draft-ready-justification-honesty
source: [14-VERIFICATION.md]
started: 2026-10-03T19:10:00Z
updated: 2026-10-04T00:45:00Z
---

## Current Test

number: 1
name: Live per-row promote (G-14-1 live re-check)
expected: |
  On live Supabase data (VITE_USE_MOCKS=false), promoting a draft material with a non-empty body via per-row
  «Сделать ready» returns HTTP 200 (not 503) and the row badge flips to «готов» after the silent refetch.
awaiting: user response

## Tests

### 1. Live per-row promote (G-14-1 live re-check)
expected: On live Supabase data (VITE_USE_MOCKS=false), promote a draft material with a non-empty body via per-row «Сделать ready»; `POST /admin/materials/{id}/ready` returns 200 (not 503) and the badge flips to «готов» after the silent refetch.
result: [pending]

### 2. Long title + ready CTA layout (14-03 backstop)
expected: Open Admin Digest with a long draft title; the title wraps with `break-words` and the draft badge + «Сделать ready» stay usable in the meta flex wrap (clickable, no overflow clipping).
result: [pending]

### 3. Long factor caption / empty justification wrap (14-03 backstop)
expected: Render a row with a long populated factor caption and a row with the exact empty sentence; both wrap with `break-words` inside `max-w-[12rem]` without breaking the shortlist row grid.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

<!-- No goal-blocking gaps after re-verification (19/20). The prior round's gaps are closed: -->
<!-- G-14-1 / G-14-4 closed by 14-06 (FK-hinted `material_relations!material_relations_from_material_id_fkey(to_material_id)` embed + offline PGRST201 regression) -->
<!-- G-14-2 closed by 14-07 (batch promote CTA + «Уберите черновики…» hint + handler/import removed; sendHint reordered; per-row control + D-85 gate intact) -->
<!-- G-14-3 closed by 14-08 (global `button:not(:disabled){cursor:pointer}` base rule + computed-cursor Playwright lock) -->

## Previous Round (closed)

The 2026-10-03T17:25Z UAT round diagnosed 4 gaps (G-14-1 blocker, G-14-2 major, G-14-3 cosmetic, G-14-4 major) and 2 passes
(tests 3 and 4). Those gaps were planned as 14-06/14-07/14-08 and are closed, verified, and regression-locked —
see `14-VERIFICATION.md` (re-verification section). Tests 2, 5 and 6 from the prior round are obsolete (the batch promote
surface they exercised was removed by 14-07).

## Deferred Follow-Ups

- test: 1
  idea: "UX (для Phase 15+): две операции на одно editorial-решение избыточны для single-operator workflow — объединить Approve (decision) + Mark ready (material_status) в одну кнопку «Одобрить и подготовить → ready»; переименовать «Сделать ready» → «Отобрать», ready → «Отобран»."
  deferred_at: 2026-10-03
