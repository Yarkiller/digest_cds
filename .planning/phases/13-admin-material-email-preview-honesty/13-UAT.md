---
status: testing
phase: 13-admin-material-email-preview-honesty
source: [13-VERIFICATION.md]
started: 2026-10-03T07:30:00Z
updated: 2026-10-03T07:30:00Z
---

## Current Test

number: 1
name: Long title / provenance wrap in material preview
expected: |
  Title and provenance wrap with break-words; close (✕) stays reachable
awaiting: user response

## Tests

### 1. Long title / provenance wrap
expected: Title and provenance wrap with break-words; close (✕) stays reachable
result: [pending]

### 2. Long markdown scroll
expected: Body scrolls inside the material preview dialog; close control remains usable
result: [pending]

### 3. Long email subject / HTML scroll
expected: Subject wraps; iframe/modal scrolls without clipping close
result: [pending]

### 4. Long connecting text + hint
expected: Textarea wraps/scrolls; muted «Пустая строка = новый абзац» stays visible below
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
