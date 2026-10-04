---
phase: 16
review: 16-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "pydantic imported directly but not declared as a dependency"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "Validator only catches MarkedYAMLError; deep documents escape as 500"
    source: "fixed in commit 758ddac (catch RecursionError -> structured 400); VERIFICATION.md re-run passed 49/49"
  - id: WR-03
    severity: warning
    disposition: open
    title: "Length cap does not mitigate YAML alias expansion as the comment claims"
  - id: WR-04
    severity: warning
    disposition: deferred
    title: "window.confirm inside beforeunload is unreliable"
    source: "accepted known limitation; promoted to ROADMAP backlog 999.6 (2026-10-04)"
  - id: WR-05
    severity: warning
    disposition: deferred
    title: "Unsaved edits are lost on in-app (SPA) navigation"
    source: "accepted known limitation; promoted to ROADMAP backlog 999.6 (2026-10-04)"
  - id: IN-01
    severity: info
    disposition: open
    title: "Playwright mock-control harness is exposed in every build"
  - id: IN-02
    severity: info
    disposition: open
    title: "Duplicate imports in test_live_container_wiring.py"
  - id: IN-03
    severity: info
    disposition: open
    title: "Mocks default to ON, so the new service silently no-ops"
  - id: IN-04
    severity: info
    disposition: open
    title: "Migration relies solely on RLS; consider revoking default grants"
open: 6
total: 9
recorded: 2026-10-04T12:05:00.000Z
---

# Phase 16: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | fixed | fixed in commit 758ddac (catch RecursionError -> structured 400) |
| WR-03 | warning | open | - |
| WR-04 | warning | deferred | accepted known limitation; ROADMAP backlog 999.6 |
| WR-05 | warning | deferred | accepted known limitation; ROADMAP backlog 999.6 |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
