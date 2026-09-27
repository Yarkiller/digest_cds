---
phase: 09
review: 09-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "RPC SQL tests still match comments, not executable statements"
  - id: WR-02
    severity: warning
    disposition: open
    title: "Conflict path can return a sent batch"
  - id: WR-03
    severity: warning
    disposition: open
    title: "Migration 007 SQL tests match a comment, not the DDL"
  - id: WR-04
    severity: warning
    disposition: open
    title: "CAP-02 test never composes captions/article with persist"
  - id: WR-05
    severity: warning
    disposition: open
    title: "Unlocked overflow can exceed p_batch_size and duplicate rank"
  - id: IN-01
    severity: info
    disposition: open
    title: "RPC does not enforce the closed RoleKind set"
  - id: IN-02
    severity: info
    disposition: open
    title: "Settings repr includes supabase_secret_key"
  - id: IN-03
    severity: info
    disposition: open
    title: "Environ-access scan skips ingestion-service adapters"
open: 7
total: 8
recorded: 2026-09-27T17:05:06.879Z
---

# Phase 09: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 09-REVIEW-FIX.md |
| WR-02 | warning | open | - (not in the current review) |
| WR-03 | warning | open | - (not in the current review) |
| WR-04 | warning | open | - (not in the current review) |
| WR-05 | warning | open | - (not in the current review) |
| IN-01 | info | open | - (not in the current review) |
| IN-02 | info | open | - (not in the current review) |
| IN-03 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
