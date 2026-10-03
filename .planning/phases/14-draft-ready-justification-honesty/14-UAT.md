---
status: complete
phase: 14-draft-ready-justification-honesty
source: [14-VERIFICATION.md]
started: 2026-10-03T14:13:45Z
updated: 2026-10-03T15:57:12Z
---

## Current Test

[testing complete]

## Tests

### 1. Long title + ready CTA layout
expected: Title wraps with break-words; badge and CTA remain clickable without overflow clipping
result: pass

### 2. Sticky footer with many approved drafts
expected: Approved-draft titles wrap/scroll within the sticky footer without covering the batch CTA hit target
result: issue
reported: "Blocker: per-row «Сделать ready» click does nothing — state unchanged (ADUX-05 core, D-85 unblock broken). UX: [draft] + одобрен reads as contradiction; footer duplicates titles + batch CTA label «одобренные черновики» confusing."
severity: blocker

### 3. Factor caption / empty justification wrap
expected: Long captions and the D-15 empty sentence wrap with break-words inside max-w-[12rem] without breaking the shortlist row grid
result: pass

## Summary

total: 3
passed: 2
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-14-2
  truth: "Per-row «Сделать ready» promotes a draft to ready, clears the D-85 send hint, and updates row state (ADUX-05)"
  status: failed
  reason: "User reported: per-row «Сделать ready» click does nothing — state unchanged; ADUX-05 core function, D-85 unblock path broken. Diagnose: Network tab for POST /admin/materials/{id}/ready; backend logs request_id; check mocks vs live."
  severity: blocker
  test: 2
  artifacts: []
  missing: []

- gap_id: G-14-2a
  truth: "Draft badge and approval state read unambiguously (no contradictory [draft] + одобрен pairing)"
  status: failed
  reason: "User reported: [draft] + одобрен reads as contradiction — tooltip or clearer labels needed"
  severity: minor
  test: 2
  artifacts: []
  missing: []

- gap_id: G-14-2b
  truth: "Sticky send footer does not duplicate approved-draft titles and the batch CTA label is unambiguous"
  status: failed
  reason: "User reported: footer duplicates titles; batch CTA label «одобренные черновики» confusing — collapse list or count-only, rename CTA"
  severity: minor
  test: 2
  artifacts: []
  missing: []
