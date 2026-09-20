---
status: testing
phase: 03-voting-cycle
source: [03-VERIFICATION.md]
started: 2026-09-20T17:05:00Z
updated: 2026-09-20T17:05:00Z
---

## Current Test

number: 1
name: Live FE↔BE ballot smoke (VITE_USE_MOCKS=false, APP_CONTAINER=live)
expected: |
  Authenticated /voting loads seeded topics with audit deks; confirm stores one vote;
  A→B updates status; closed reject shows «Цикл голосования закрыт»
awaiting: user response

## Tests

### 1. Live FE↔BE ballot smoke
expected: Authenticated /voting loads seeded topics with audit deks; confirm stores one vote; A→B updates status; closed reject shows «Цикл голосования закрыт»
result: [pending]

### 2. UI-SPEC visual backstops
expected: Leader strip, topic rows, and status reflow at 320/390/1280 without clipping or false empty/closed flash
result: [pending]

### 3. Reconfirm live DDL trigger on shared VM
expected: pg_trigger lists votes_enforce_open_and_topic; closed-cycle write rejected at DB as well as app layer
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
