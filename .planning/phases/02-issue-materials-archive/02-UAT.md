---
status: testing
phase: 02-issue-materials-archive
source: [02-VERIFICATION.md]
started: 2026-09-20T11:30:00Z
updated: 2026-09-20T11:30:00Z
---

## Current Test

number: 1
name: UI-SPEC visual backstops (held-out)
expected: |
  IssueTOC/archive/material/callout/hero/nav pass overflow, plural, and mobile reflow checks in 02-UI-SPEC
  At 320/390/1280: no broken overflow; Russian plural captions for 1/2/5+; 44px hit targets; nav clear of wordmark
awaiting: user response

## Tests

### 1. UI-SPEC visual backstops (held-out)
expected: IssueTOC/archive/material/callout/hero/nav pass overflow, plural, and mobile reflow checks in 02-UI-SPEC (320/390/1280 viewports)
result: [pending]

### 2. Live FE↔BE smoke (VITE_USE_MOCKS=false)
expected: Authenticated `/` shows issue №14 typography hero + TOC; `/materials/rag-systems` shows Статья + prose + TOC; `/archive` lists №13 → `/issues/13` without callout
result: [pending]

### 3. Advisory: live tags + open-cycle clock (02-REVIEW WR-01, WR-03)
expected: Tag chips show display labels (not slugs); callout open/closed matches editorial intent after closes_at
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
