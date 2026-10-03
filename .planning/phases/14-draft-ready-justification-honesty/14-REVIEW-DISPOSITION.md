---
phase: 14
review: 14-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`honest_factor_labels` fabricates labels for non-string structured entries"
  - id: WR-02
    severity: warning
    disposition: open
    title: "Live `markReady` still ties promote success to JSON parsing — residual silent revert"
  - id: WR-03
    severity: warning
    disposition: open
    title: "Batch reconcile (the same silent-revert class) is not behaviorally tested"
  - id: IN-01
    severity: info
    disposition: open
    title: "Source-text assertions couple wiring tests to implementation"
  - id: IN-02
    severity: info
    disposition: open
    title: "Footer `locator(\"ul\")` assertion is a weak proxy for \"no duplicate titles\""
  - id: IN-03
    severity: info
    disposition: open
    title: "`MarkReadyBatchRequest.material_ids` remains unbounded"
  - id: IN-04
    severity: info
    disposition: open
    title: "Broad `except Exception` in the batch masks unexpected failures"
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Live `markReady` rolls back UI after successful promote when shortlist refetch fails"
open: 7
total: 8
recorded: 2026-10-03T17:10:00.000Z
---

# Phase 14: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| CR-01 | critical | fixed | 14-REVIEW-FIX.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.

Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.

Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

Dropped on this run (id reused by a different finding): WR-01=fixed, WR-02=fixed. IN-01=open and IN-02=open were replaced silently (no decision to lose).
