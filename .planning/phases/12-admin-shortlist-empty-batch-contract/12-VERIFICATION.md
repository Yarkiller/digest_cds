---
phase: 12-admin-shortlist-empty-batch-contract
verified: 2026-10-03T20:59:00Z
status: passed
score: 12/12 must-haves verified
covered_files:
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-01-PLAN.md
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-01-SUMMARY.md
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-02-PLAN.md
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-02-SUMMARY.md
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-03-PLAN.md
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-03-SUMMARY.md
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-CONTEXT.md
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-FIX-01-LOCK.md
  - tests/admin.spec.js
  - tests/unit/test_http_admin.py
  - web/src/services/adminApi.js
covered_digest: "v2:sha256:32d45875289b72c6d27db7ea3f1c1a2b737edcba92272512712e8fa2bd7b9fff"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 8/8
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 12: Admin shortlist empty-batch contract Verification Report

**Phase Goal:** Empty admin shortlist responses match the locked HTTP contract so the Phase 10 carry unit passes
**Verified:** 2026-10-03T20:59:00Z
**Status:** passed
**Re-verification:** Yes — stale-digest re-verification (GSD #4682). The prior report claims `passed` 8/8; its `covered_digest` no longer matches because the covered source files gained Phase 13/14 additions after it was written. This report is regenerated from the CURRENT codebase with a fresh digest. No prior `gaps:` existed.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ------- | ------ | -------------- |
| 1 | Both FIX-01 proof tests exist and are green: `test_admin_shortlist_no_batches_returns_null_batch_id` and `test_admin_shortlist_empty_unsent_batch_returns_batch_id` (SC1 / D-05) | ✓ VERIFIED | `uv run pytest tests/unit/test_http_admin.py::test_admin_shortlist_no_batches_returns_null_batch_id ...::test_admin_shortlist_empty_unsent_batch_returns_batch_id -q` → **2 passed** (0.98s); old name `test_admin_shortlist_empty_batch_returns_200_empty_items` absent from `tests/` |
| 2 | No-batch `GET /admin/shortlist` returns HTTP 200, `items=[]`, `batch_id` null, `week_label` null, `sent_at` null, `digest_rest` false, `days_until_next_batch` null under required-key asserts (D-04 #1 / D-08) | ✓ VERIFIED | `test_admin_shortlist_no_batches_returns_null_batch_id` seeds `InMemoryShortlistRepository(batch=None)`, asserts all six required keys present plus the exact null/[]/false values; HTTP 200 |
| 3 | Empty-unsent `GET /admin/shortlist` returns HTTP 200, `items=[]`, `batch_id` int, `week_label=week_start.isoformat()`, `sent_at` null, `digest_rest` false, `days_until_next_batch` null (D-04 #2 / D-06) | ✓ VERIFIED | `test_admin_shortlist_empty_unsent_batch_returns_batch_id` seeds `ShortlistBatch(id=7, week_start=date(2026,10,6), sent_at=None, items=())`; asserts `batch_id == 7`, `week_label == "2026-10-06"`, `items == []`, `sent_at is None`, `digest_rest is False` |
| 4 | The two empty edges stay distinct — `batch_id` null-vs-int and `week_label` null-vs-ISO — never collapsed (D-04) | ✓ VERIFIED | No-batch asserts `batch_id is None` + `week_label is None`; empty-unsent asserts `batch_id == 7` + `week_label == "2026-10-06"`. Distinct assertions in the two named tests |
| 5 | Empty responses never surface as a schema/validation HTTP 500 and `AdminShortlistResponse` keeps `extra="forbid"` (D-09 / SC3) | ✓ VERIFIED | Both tests assert `status_code == 200`; `AdminShortlistResponse` declares `model_config = ConfigDict(extra="forbid")` at `admin.py:60` and every declared field; `_to_response` passes only declared fields |
| 6 | Contract fields (`batch_id`, `items`, `week_label`, `sent_at`, `digest_rest`, `days_until_next_batch`) align so clients are not blocked by missing/extra schema noise (SC3) | ✓ VERIFIED | Both tests loop-assert every required key is present; the response model declares exactly those six fields under `extra="forbid"`, so undeclared extras cannot serialize |
| 7 | FIX-01 empty-edge coverage is in-memory HTTP units only — no live Supabase (D-07) | ✓ VERIFIED | Both tests use `build_in_memory_container()` + `InMemoryShortlistRepository`; `_client` uses empty Supabase settings and a local signing-key resolver — no network |
| 8 | Scope-bound green (D-02): Phase 12 introduces no new suite failures | ✓ VERIFIED | `uv run pytest -q` → **684 passed**, 1 warning, 5.15s |
| 9 | `12-FIX-01-LOCK.md` documents both D-04 empty shapes and the D-08 required-key assert rules (D-10) | ✓ VERIFIED | Lock file present: Shape 1 (no-batches) and Shape 2 (empty-unsent) tables; "Forbidden: brittle full-body JSON equality"; `extra="forbid"` posture; digest_rest third-shape note; both D-05 proof names |
| 10 | `REQUIREMENTS.md` FIX-01 cites both D-05 proof names and is marked Complete (D-05) | ✓ VERIFIED | `REQUIREMENTS.md:33-36` — FIX-01 `[x]` cites both `test_admin_shortlist_no_batches_returns_null_batch_id` and `test_admin_shortlist_empty_unsent_batch_returns_batch_id`; Traceability `FIX-01 → Phase 12 Complete` |
| 11 | `ROADMAP.md` Phase 12 Success Criterion #1 and `PROJECT.md` cite both D-05 names (not the pre-rename sole name) (D-05) | ✓ VERIFIED | `ROADMAP.md:61` cites both; `PROJECT.md:30` and `PROJECT.md:87` cite both. Old sole name `test_admin_shortlist_empty_batch_returns_200_empty_items` absent from `.planning` active docs |
| 12 | FE mock harness exposes `__DIGEST_ADMIN_EMPTY_UNSENT__` → `emptyUnsentDto` (batch_id 7, ISO week_label, items=[], digest_rest false); `resetAdminHarness` clears it; `__DIGEST_ADMIN_EMPTY__` stays no-batch; Playwright empty-unsent shows D-80 empty UI with zero пайплайн / digest_rest and no new chrome (D-11…D-13) | ✓ VERIFIED | `adminApi.js`: `emptyUnsentDto()` + fetch branch order DIGEST_REST → EMPTY_UNSENT → EMPTY + `resetAdminHarness` sets `window.__DIGEST_ADMIN_EMPTY_UNSENT__ = false`. `AdminDigestPage.jsx` has no `__DIGEST_ADMIN_EMPTY_UNSENT__` special-case (D-13 unchanged). `npx playwright test --project=web tests/admin.spec.js --grep EMPTY_UNSENT` → **1 passed** (4.5s) |

**Score:** 12/12 truths verified (0 present, behavior-unverified)

### Deferred Items

None. `12-FIX-01-LOCK.md` gained additive Phase 13 item-schema rows (ADUX-01) and a Phase 13 ban-list section after the prior verification; those are documented later-phase growth, not Phase 12 scope, and they do not alter Shapes 1–2 or the D-08/09 posture.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `tests/unit/test_http_admin.py` | Renamed no-batch + new empty-unsent FIX-01 proofs | ✓ VERIFIED | Both node ids present with required-key asserts; both green this pass |
| `backend/.../get_admin_shortlist.py` | No-batch / empty-unsent branches | ✓ VERIFIED | `batch is None` → null shape; current unsent batch → `batch_id`, `week_label=batch.week_start.isoformat()`, `sent_at=batch.sent_at`; unchanged by Phase 12 (D-03) |
| `backend/.../routes/admin.py` | `AdminShortlistResponse` + `_to_response` | ✓ VERIFIED | `extra="forbid"`; all six contract fields declared; `Depends(require_admin)` retained |
| `12-FIX-01-LOCK.md` | Authoritative empty-shape tables | ✓ VERIFIED | Shapes 1–2 + D-08 rules + D-09 posture + D-05 names |
| `.planning/REQUIREMENTS.md` | FIX-01 proof strings | ✓ VERIFIED | Both D-05 names; Complete |
| `.planning/ROADMAP.md` | Phase 12 SC proof names | ✓ VERIFIED | SC #1 cites both; SC #2–#3 retained |
| `.planning/PROJECT.md` | Checklist proof-string alignment | ✓ VERIFIED | Both D-05 names in target features + Active checklist |
| `web/src/services/adminApi.js` | `emptyUnsentDto` + sticky flag + reset clear | ✓ VERIFIED | DTO matches D-04 #2; branch order correct; reset clears flag |
| `tests/admin.spec.js` | Playwright empty-unsent case | ✓ VERIFIED | `EMPTY_UNSENT` case at `tests/admin.spec.js:145`; green this pass |
| `web/src/pages/AdminDigestPage.jsx` | Touched only if TDD forced (D-13) | ✓ VERIFIED (untouched by Phase 12) | `showTriage = !restMode && items.length > 0` reuses D-80 empty UI; no empty-unsent special-case; Phase 13/14 edits unrelated to this phase's contract |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `InMemoryShortlistRepository(batch=None \| ShortlistBatch items=())` | `AdminShortlistResponse` JSON | `get_admin_shortlist` → `_to_response` | ✓ WIRED | Named HTTP tests seed the in-memory repo, mint admin JWT, GET `/admin/shortlist`, and receive 200 with distinct `batch_id` null vs int |
| `gotoAsRole __DIGEST_ADMIN_EMPTY_UNSENT__` | Admin empty-state UI | `adminApi.fetchShortlist` mock branch → `AdminDigestPage` | ✓ WIRED | Playwright EMPTY_UNSENT passed with `Кандидатов пока нет` heading and `admin-digest-rest` count 0 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| HTTP no-batch unit | `body["batch_id"]` / `items` | `InMemoryShortlistRepository(batch=None)` → no-batch branch | Yes (null shape) | ✓ FLOWING |
| HTTP empty-unsent unit | `body["batch_id"]` / `week_label` / `items` | `InMemoryShortlistRepository(ShortlistBatch(id=7, items=()))` → use-case | Yes (seeded id=7, ISO label) | ✓ FLOWING |
| FE EMPTY_UNSENT mock | `emptyUnsentDto()` | Sticky `window.__DIGEST_ADMIN_EMPTY_UNSENT__` in `fetchShortlist` mock path | Yes (harness DTO matching D-04 #2) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| FIX-01 HTTP proof pair | `uv run pytest tests/unit/test_http_admin.py::test_admin_shortlist_no_batches_returns_null_batch_id tests/unit/test_http_admin.py::test_admin_shortlist_empty_unsent_batch_returns_batch_id -q` | 2 passed, 1 warning (0.98s) | ✓ PASS |
| Full backend suite (scope-bound green) | `uv run pytest -q` | 684 passed (5.15s) | ✓ PASS |
| Playwright empty-unsent E2E | `npx playwright test --project=web tests/admin.spec.js --grep EMPTY_UNSENT` | 1 passed (4.5s) | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| FIX-01 | 12-01, 12-02, 12-03 | no-batch + empty-unsent HTTP contracts (D-04) green under required-key asserts — both D-05 proof names | ✓ SATISFIED | Truths 1–12: unit pair green, `extra=forbid` retained, lock doc, REQUIREMENTS/ROADMAP/PROJECT proof strings, FE harness + Playwright |

Orphaned requirements for Phase 12: **none**. `REQUIREMENTS.md` maps only FIX-01 to Phase 12; every plan frontmatter `requirements:` list is `[FIX-01]`.

### Prohibitions (judgment-tier — re-checked in code this pass)

| Statement | Verdict | Evidence |
| --------- | ------- | -------- |
| MUST NOT return schema/validation HTTP 500 for empty shortlist responses | ✓ held | Both empty-edge units assert HTTP 200 |
| MUST NOT collapse no-batch and empty-unsent into one HTTP shape | ✓ held | Distinct `batch_id` null-vs-int + `week_label` null-vs-ISO asserts |
| MUST NOT weaken `AdminShortlistResponse` `extra="forbid"` | ✓ held | `ConfigDict(extra="forbid")` at `admin.py:60` (and on the item model) |
| MUST NOT use live Supabase for FIX-01 unit proofs | ✓ held | `build_in_memory_container()` + `InMemoryShortlistRepository`; no network in the named tests |
| MUST NOT document a collapsed single empty shape | ✓ held | Lock keeps Shape 1 / Shape 2 distinct |
| MUST NOT leave REQUIREMENTS/ROADMAP citing only the pre-rename sole proof name | ✓ held | Both D-05 names present; old name absent from active docs |
| MUST NOT treat the digest_rest mock as empty-unsent (or vice versa) | ✓ held | Branch precedence DIGEST_REST → EMPTY_UNSENT → EMPTY; EMPTY_UNSENT Playwright asserts `admin-digest-rest` count 0 |
| MUST NOT leave `__DIGEST_ADMIN_EMPTY_UNSENT__` sticky across tests after `resetAdminHarness` | ✓ held | `resetAdminHarness` sets the flag to `false` |
| MUST NOT invent new empty-state copy/chrome for empty-unsent unless TDD forces it | ✓ held | `AdminDigestPage.jsx` has no empty-unsent branch; D-80 empty UI reused; no production page edit in Phase 12 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `12-FIX-01-LOCK.md` | 8–27 | Phase 13 additive item-schema / ban-list sections | ℹ️ Info | Later-phase growth documented in the lock under ADUX-01 / ADUX-04; Shapes 1–2 and D-08/D-09 unchanged |
| phase-modified sources | — | No `TBD` / `FIXME` / `XXX` / `TODO` debt markers (`test_http_admin.py`, `adminApi.js`, `get_admin_shortlist.py` grep) | — | None |

### Human Verification Required

None. Every must-have has automated behavioral evidence (named HTTP units executed this pass + the Playwright empty-unsent case executed this pass). No PLAN `<human-check>` blocks exist in the phase plans, and no truth is behavior-unverified.

### Gaps Summary

No gaps. Phase goal achieved: the locked empty admin shortlist HTTP contract is present and behaviorally proven — both empty shapes return HTTP 200 with distinct `batch_id`/`week_label`, proven by the D-05 unit pair; `extra="forbid"` is retained; the lock doc and REQUIREMENTS/ROADMAP/PROJECT proof strings cite both names; and the FE mock harness + Playwright empty-unsent path reuse the D-80 empty UI without digest_rest or new chrome. Full backend suite is green (684 passed).

---

_Verified: 2026-10-03T20:59:00Z_
_Verifier: Claude (gsd-verifier)_
