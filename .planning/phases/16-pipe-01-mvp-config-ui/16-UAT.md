---
status: testing
phase: 16-pipe-01-mvp-config-ui
source: [16-VERIFICATION.md]
started: 2026-10-04T12:15:00.000Z
updated: 2026-10-04T12:15:00.000Z
---

## Current Test

number: 1
name: Live persistence round-trip (PIPE-03 DoD)
expected: |
  In live mode (VITE_USE_MOCKS=false against the shared VM), open /admin/pipeline as admin,
  save a valid YAML document, reload, and confirm the saved YAML is returned. The saved
  document is persisted to public.pipeline_config (id=1) and read back on a subsequent admin
  session; count becomes 1.
awaiting: user response

## Tests

### 1. Live persistence round-trip (PIPE-03 DoD)
expected: In live mode (VITE_USE_MOCKS=false against the shared VM), open /admin/pipeline as admin, save a valid YAML document, reload, and confirm the saved YAML is returned; the row persists to public.pipeline_config (id=1) with count 1.
result: [pending]

### 2. Visual overflow/backstop checks on /admin/pipeline (7 items)
expected: Editor scrolls internally on a long config; the Save toolbar stays reachable and never overlaps; the error panel wraps long text; the nav item stays usable at narrow widths.
result: [pending]

### 3. Unsaved-changes guard in a real browser (WR-04/WR-05)
expected: After editing the YAML, (a) closing/reloading the tab and (b) clicking an in-app NavLink (e.g. «Архив») presents a leave-confirm; Cancel keeps the edit. NOTE: the code uses window.confirm inside beforeunload (unreliable in real browsers) and registers no router-level guard, so in-app SPA navigation currently discards the draft without a prompt.
result: [pending]

### 4. Deep-nesting robustness (WR-02)
expected: PUT a config of ~3000 nested flow brackets (under the 20k cap) returns a structured 400 {errors:[...]}. NOTE: the live probe returned an unhandled RecursionError (HTTP 500) rather than a structured reject — decide whether to fix now or accept as a known robustness gap (no write occurs either way, so "no silent accept" holds).
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
