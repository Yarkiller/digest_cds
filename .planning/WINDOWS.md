---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-09-19T15:26:47.454Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 01 | deviation | README.md |  | Auth dashboard corporate test-user seed deferred to Plan 01-06 (D-08) | open |  | 2026-09-19T15:26:47.454Z |  |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "01",
    "file": "README.md",
    "line": null,
    "description": "Auth dashboard corporate test-user seed deferred to Plan 01-06 (D-08)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-19T15:26:47.454Z",
    "resolved_at": null
  }
]
````
