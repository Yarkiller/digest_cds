---
schema_version: 1
open_count: 3
waived_count: 0
fixed_count: 0
total_count: 3
last_updated: 2026-09-20T11:09:43.276Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 01 | deviation | README.md |  | Auth dashboard corporate test-user seed deferred to Plan 01-06 (D-08) | open |  | 2026-09-19T15:26:47.454Z |  |
| 2 | 01 | deviation | playwright.config.js |  | Expanded web testMatch to include auth.spec.js so Plan 01-05 verify can run | open |  | 2026-09-19T15:32:14.897Z |  |
| 3 | 02 | skipped-test | tests/web-app.spec.js | 406 | UI-SPEC visual backstops describe.skip held for /gsd-verify-work | open |  | 2026-09-20T11:09:43.276Z |  |

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
  },
  {
    "id": 2,
    "kind": "deviation",
    "phase": "01",
    "file": "playwright.config.js",
    "line": null,
    "description": "Expanded web testMatch to include auth.spec.js so Plan 01-05 verify can run",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-19T15:32:14.897Z",
    "resolved_at": null
  },
  {
    "id": 3,
    "kind": "skipped-test",
    "phase": "02",
    "file": "tests/web-app.spec.js",
    "line": 406,
    "description": "UI-SPEC visual backstops describe.skip held for /gsd-verify-work",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-20T11:09:43.276Z",
    "resolved_at": null
  }
]
````
