---
status: testing
phase: 04-knowledge-razbory
source: [04-VERIFICATION.md]
started: 2026-09-21T09:50:00Z
updated: 2026-09-21T09:50:00Z
---

## Current Test

number: 1
name: UI-SPEC overflow / long-text backstops (pagination, many chronology, title wrap, TOC layout)
expected: |
  No clipped CTAs; titles wrap; sticky/mobile TOC usable without horizontal overflow
awaiting: user response

## Tests

### 1. UI-SPEC overflow / long-text backstops
expected: No clipped CTAs; titles wrap; sticky/mobile TOC usable without horizontal overflow at 320/390/1280
result: [pending]

### 2. Visual honesty: snippets without scores; chronology pattern; dual notebook strip placement
expected: Matches design-frontend chronology + notebook strip canon; no score chrome on knowledge hits
result: [pending]

### 3. Optional live FE↔BE smoke (runbook §5b)
expected: Authenticated knowledge search + razbory consume work against live FastAPI/Supabase after 004 seed (mocks off)
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
