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
    title: "Live `markReady` still rolls a persisted promote back on JSON parse failure"
  - id: WR-03
    severity: warning
    disposition: open
    title: "The PGRST201 regression test does not lock the FK hint name"
  - id: IN-01
    severity: info
    disposition: open
    title: "Batch-promote client/harness surface is now dead code"
  - id: IN-02
    severity: info
    disposition: open
    title: "`_filter_ready_relations` couples per-related lookup failures to the whole read"
  - id: IN-03
    severity: info
    disposition: open
    title: "`MarkReadyBatchRequest.material_ids` is unbounded"
  - id: IN-04
    severity: info
    disposition: open
    title: "Broad `except Exception` in batch promote masks defects without logging"
  - id: IN-05
    severity: info
    disposition: open
    title: "Mock `sendDigest` order validation is weaker than the backend"
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Live `markReady` rolls back UI after successful promote when shortlist refetch fails"
open: 8
total: 9
recorded: 2026-10-03T19:05:00.000Z
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
| IN-05 | info | open | - |
| CR-01 | critical | fixed | 14-REVIEW-FIX.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.

Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.

Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

The re-review renumbered/narrowed several ids: WR-03, IN-01, IN-02, IN-03 and IN-04 now name different findings than the previous ledger recorded (all previously `open`, so no decision was lost). The fix report's WR-01 and WR-02 entries title their findings differently from the current review, so they were not reconciled into rows — CR-01 is the only carried, fixed finding.
