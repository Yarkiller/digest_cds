---
schema_version: 1
open_count: 14
waived_count: 0
fixed_count: 3
total_count: 17
last_updated: 2026-10-02T13:36:12.392Z
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
| 4 | 04 | stub | backend/src/backend/application/ports/query_embedder.py |  | StubQueryEmbedder deterministic hash embedder, not Foundry HTTP (Phase 4 OPT-OUT) | open |  | 2026-09-21T04:34:37.222Z |  |
| 5 | 04 | stub | backend/src/backend/composition/live.py |  | live.py chunks still InMemoryKnowledgeChunkRepository until 04-08 | open |  | 2026-09-21T04:34:37.841Z |  |
| 6 | 04 | skipped-test | tests/web-app.spec.js |  | Knowledge Playwright tests still assert client filterMaterials/tag facets; rewrite deferred to 04-09 | fixed |  | 2026-09-21T04:40:59.311Z | 2026-09-21T05:04:04.951Z |
| 7 | 04 | deviation | web/src/services/knowledgeApi.js |  | Dynamic import of authEnv/authApi so mockSearchKnowledge stays node:test-friendly without Vite env | open |  | 2026-09-21T04:40:59.943Z |  |
| 8 | 04 | stub | backend/src/backend/application/use_cases/get_razbor.py |  | get_razbor NotFound only; detail HTTP deferred to 04-06 | open |  | 2026-09-21T04:45:39.748Z |  |
| 9 | 04 | stub | backend/src/backend/composition/live.py |  | live.py razbors still InMemoryRazborRepository until adapter | open |  | 2026-09-21T04:45:40.363Z |  |
| 10 | 04 | deviation | tests/web-app.spec.js |  | Retired Загрузить ещё Playwright case; mock catalog is smaller than page size 10 | open |  | 2026-09-21T05:02:21.685Z |  |
| 11 | 04 | stub | web/src/App.jsx |  | /razbory/:id placeholder shell until 04-06 | open |  | 2026-09-21T05:12:01.843Z |  |
| 12 | 04 | stub | tests/ |  | Playwright razbory list/empty/nav deferred to 04-09 | fixed |  | 2026-09-21T05:12:02.428Z | 2026-09-21T09:25:00.909Z |
| 13 | 04 | stub | tests/web-app.spec.js |  | Playwright notebook enable/disable proofs deferred to 04-09 | fixed |  | 2026-09-21T05:25:32.263Z | 2026-09-21T09:25:01.654Z |
| 14 | 04 | unmet-truth | .planning/phases/04-knowledge-razbory/04-VALIDATION.md |  | UI-SPEC overflow/long-text backstops held for verify-work (pagination has_more, many chronology, visual wrap) | open |  | 2026-09-21T09:25:10.848Z |  |
| 15 | 05 | deviation | web/src/services/adminPreviewComposition.js |  | Extracted pure composition helpers for node --test (Vite import.meta boundary) | open |  | 2026-09-21T18:31:58.934Z |  |
| 16 | 10 | deviation | ingestion-service/src/ingestion_service/application/ports/persist.py |  | already_saved defaults False for deferred 10-05 call sites | open |  | 2026-09-29T17:58:41.951Z |  |
| 17 | 11 | deviation | tests/unit/test_cli_ingest_contract.py |  | Unexpected GREEN Task1: CLI sent-batch contract passed without cli.py change (prior plans) | open |  | 2026-10-02T13:36:12.392Z |  |

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
  },
  {
    "id": 4,
    "kind": "stub",
    "phase": "04",
    "file": "backend/src/backend/application/ports/query_embedder.py",
    "line": null,
    "description": "StubQueryEmbedder deterministic hash embedder, not Foundry HTTP (Phase 4 OPT-OUT)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T04:34:37.222Z",
    "resolved_at": null
  },
  {
    "id": 5,
    "kind": "stub",
    "phase": "04",
    "file": "backend/src/backend/composition/live.py",
    "line": null,
    "description": "live.py chunks still InMemoryKnowledgeChunkRepository until 04-08",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T04:34:37.841Z",
    "resolved_at": null
  },
  {
    "id": 6,
    "kind": "skipped-test",
    "phase": "04",
    "file": "tests/web-app.spec.js",
    "line": null,
    "description": "Knowledge Playwright tests still assert client filterMaterials/tag facets; rewrite deferred to 04-09",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-21T04:40:59.311Z",
    "resolved_at": "2026-09-21T05:04:04.951Z"
  },
  {
    "id": 7,
    "kind": "deviation",
    "phase": "04",
    "file": "web/src/services/knowledgeApi.js",
    "line": null,
    "description": "Dynamic import of authEnv/authApi so mockSearchKnowledge stays node:test-friendly without Vite env",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T04:40:59.943Z",
    "resolved_at": null
  },
  {
    "id": 8,
    "kind": "stub",
    "phase": "04",
    "file": "backend/src/backend/application/use_cases/get_razbor.py",
    "line": null,
    "description": "get_razbor NotFound only; detail HTTP deferred to 04-06",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T04:45:39.748Z",
    "resolved_at": null
  },
  {
    "id": 9,
    "kind": "stub",
    "phase": "04",
    "file": "backend/src/backend/composition/live.py",
    "line": null,
    "description": "live.py razbors still InMemoryRazborRepository until adapter",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T04:45:40.363Z",
    "resolved_at": null
  },
  {
    "id": 10,
    "kind": "deviation",
    "phase": "04",
    "file": "tests/web-app.spec.js",
    "line": null,
    "description": "Retired Загрузить ещё Playwright case; mock catalog is smaller than page size 10",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T05:02:21.685Z",
    "resolved_at": null
  },
  {
    "id": 11,
    "kind": "stub",
    "phase": "04",
    "file": "web/src/App.jsx",
    "line": null,
    "description": "/razbory/:id placeholder shell until 04-06",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T05:12:01.843Z",
    "resolved_at": null
  },
  {
    "id": 12,
    "kind": "stub",
    "phase": "04",
    "file": "tests/",
    "line": null,
    "description": "Playwright razbory list/empty/nav deferred to 04-09",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-21T05:12:02.428Z",
    "resolved_at": "2026-09-21T09:25:00.909Z"
  },
  {
    "id": 13,
    "kind": "stub",
    "phase": "04",
    "file": "tests/web-app.spec.js",
    "line": null,
    "description": "Playwright notebook enable/disable proofs deferred to 04-09",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-21T05:25:32.263Z",
    "resolved_at": "2026-09-21T09:25:01.654Z"
  },
  {
    "id": 14,
    "kind": "unmet-truth",
    "phase": "04",
    "file": ".planning/phases/04-knowledge-razbory/04-VALIDATION.md",
    "line": null,
    "description": "UI-SPEC overflow/long-text backstops held for verify-work (pagination has_more, many chronology, visual wrap)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T09:25:10.848Z",
    "resolved_at": null
  },
  {
    "id": 15,
    "kind": "deviation",
    "phase": "05",
    "file": "web/src/services/adminPreviewComposition.js",
    "line": null,
    "description": "Extracted pure composition helpers for node --test (Vite import.meta boundary)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-21T18:31:58.934Z",
    "resolved_at": null
  },
  {
    "id": 16,
    "kind": "deviation",
    "phase": "10",
    "file": "ingestion-service/src/ingestion_service/application/ports/persist.py",
    "line": null,
    "description": "already_saved defaults False for deferred 10-05 call sites",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-29T17:58:41.951Z",
    "resolved_at": null,
    "milestone": "v1.1"
  },
  {
    "id": 17,
    "kind": "deviation",
    "phase": "11",
    "file": "tests/unit/test_cli_ingest_contract.py",
    "line": null,
    "description": "Unexpected GREEN Task1: CLI sent-batch contract passed without cli.py change (prior plans)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-10-02T13:36:12.392Z",
    "resolved_at": null,
    "milestone": "v1.1"
  }
]
````
