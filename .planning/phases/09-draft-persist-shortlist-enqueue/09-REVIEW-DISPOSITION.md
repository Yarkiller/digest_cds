---
phase: 09
review: 09-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "Conflict path returns the caller slug, not the stored slug"
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
open: 8
total: 8
recorded: 2026-09-27T16:09:00Z
---

# Phase 09: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved.
