---
status: testing
phase: 14-draft-ready-justification-honesty
source: [14-VERIFICATION.md]
started: 2026-10-03T17:25:00Z
updated: 2026-10-03T17:25:00Z
---

## Current Test

number: 1
name: Long title + ready CTA layout
expected: |
  Title wraps with break-words; badge and CTA remain clickable without overflow clipping
awaiting: user response

## Tests

### 1. Long title + ready CTA layout
expected: Title wraps with break-words; draft badge and «Сделать ready» remain clickable without overflow clipping
result: [pending]

### 2. Sticky footer with many approved drafts
expected: With N≥2 approved drafts, the count-only hint and «Сделать ready все одобренные черновики (N)» CTA remain visible and hit-testable without covering each other (footer no longer re-lists titles — 14-05 / G-14-2b)
result: [pending]

### 3. Factor caption / empty justification wrap
expected: Long captions and the D-15 empty sentence wrap with break-words inside max-w-[12rem] without breaking the shortlist row grid
result: [pending]

### 4. Per-row promote failure rollback (D-05)
expected: A toast is shown and the row rolls back to «черновик» (no fake ready)
why_human: Rollback-on-failure state transition; no failure-injection exists for markReady and no test exercises the promote-failure branch — happy path only is Playwright-covered
result: [pending]

### 5. Batch partial-failure rollback (D-08)
expected: ok ids become «готов»; failed ids stay «черновик» with a toast listing them
why_human: Rollback of failed ids is a state transition; the batch Playwright case exercises only the all-ok path
result: [pending]

### 6. Batch stale-refetch no-clobber (G-14-2 batch half / 14-REVIEW WR-03)
expected: Promoted ok ids stay «готов» after a stale batch refetch (backend acks but the shortlist still reports draft)
why_human: The __DIGEST_ADMIN_STALE_READY__ harness is honoured only by the single markReady mock; the batch preservePromotedReady call is asserted only by a source-text regex
result: [pending]

## Summary

total: 6
passed: 0
issues: 0
pending: 6
skipped: 0
blocked: 0

## Gaps
