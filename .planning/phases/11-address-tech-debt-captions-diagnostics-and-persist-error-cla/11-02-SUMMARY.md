---
phase: 11-address-tech-debt-captions-diagnostics-and-persist-error-cla
plan: 02
subsystem: api
tags: [persist, postgrest, error-classification, rpc]

requires:
  - phase: 09-draft-persist-shortlist-enqueue
    provides: PERSIST_REASONS, DraftPersist* errors, map_persist_error
  - phase: 10-cli-composition-uat
    provides: SupabaseDraftPersister classification frozensets
provides:
  - SQLSTATE 23514 → batch_creation_failed (alongside check_violation)
  - int HTTP gateway code → rpc_error (D-06)
affects:
  - 11-03 sent-batch RPC
  - operator persist stderr reasons

actuals:
  tokens: 800
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "_BATCH_CODES includes both check_violation name and SQLSTATE 23514"
    - "_http_status_code(int) → DraftPersistRpcError before generic sdk fallthrough"

key-files:
  created: []
  modified:
    - ingestion-service/src/ingestion_service/adapters/supabase_persist.py
    - tests/unit/test_supabase_draft_persister_contract.py

key-decisions:
  - "Keep PERSIST_REASONS unchanged (D-07); classification-only fix"
  - "Int HTTP → rpc_error per D-06 (not network_error from Phase 10 REVIEW)"

patterns-established:
  - "String SDK codes via _sdk_code; int HTTP via _http_status_code"

requirements-completed: [PERS-02]

coverage:
  - id: D1
    description: SQLSTATE 23514 classifies as batch_creation_failed like check_violation
    requirement: PERS-02
    verification:
      - kind: unit
        ref: tests/unit/test_supabase_draft_persister_contract.py::test_sqlstate_23514_maps_to_batch_error
        status: pass
    human_judgment: false
  - id: D2
    description: Numeric HTTP 503 classifies as rpc_error
    requirement: PERS-02
    verification:
      - kind: unit
        ref: tests/unit/test_supabase_draft_persister_contract.py::test_int_http_503_maps_to_rpc_error_not_network
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-10-02
status: complete
---

# Phase 11: Plan 02 Summary

**Persist adapter now recognizes SQLSTATE `23514` and integer HTTP gateway statuses without changing `PERSIST_REASONS`.**

## Performance

- **Duration:** ~15 min
- **Tasks:** 2
- **Commits:** 4 (RED/GREEN pairs for 23514 and int HTTP)

## Accomplishments

- `_BATCH_CODES` includes `"23514"` next to `"check_violation"` / `"P0001"`
- `_http_status_code` maps int PostgREST `code` to `DraftPersistRpcError` / `rpc_error`
- Contract tests lock both edges; frozenset of persist reasons unchanged

## Deviations

None — matches D-06 / D-07.

## Self-Check: PASSED
