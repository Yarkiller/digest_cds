---
phase: "12"
slug: "admin-shortlist-empty-batch-contract"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-02"
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Python units) + Playwright (admin E2E) |
| **Config file** | root `pyproject.toml` `[tool.pytest.ini_options]`; Playwright via root `package.json` |
| **Quick run command** | `uv run pytest tests/unit/test_http_admin.py::test_admin_shortlist_no_batches_returns_null_batch_id tests/unit/test_http_admin.py::test_admin_shortlist_empty_unsent_batch_returns_batch_id -x` |
| **Full suite command** | `uv run pytest tests/unit/test_http_admin.py -q` and Playwright empty / empty-unsent cases |
| **Estimated runtime** | ~30–90 seconds (unit pair); longer for Playwright |

---

## Sampling Rate

- **After every task commit:** Run quick FIX-01 pytest pair above
- **After every plan wave:** Run `uv run pytest tests/unit/test_http_admin.py -q` + Playwright empty/empty-unsent cases
- **Before `/gsd-verify-work`:** FIX-01 pair green; lock doc present; no new suite failures introduced (D-02)
- **Max feedback latency:** 90 seconds (unit); Playwright separately

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | FIX-01 | T-12-01 / T-12-03 | Empty-unsent HTTP 200; required keys; no schema 500 | unit | `uv run pytest tests/unit/test_http_admin.py::test_admin_shortlist_empty_unsent_batch_returns_batch_id -x` | ❌ W0 | ⬜ pending |
| 12-01-02 | 01 | 1 | FIX-01 | T-12-01 | No-batch rename + required-key asserts; both proofs green | unit | `uv run pytest tests/unit/test_http_admin.py::test_admin_shortlist_no_batches_returns_null_batch_id tests/unit/test_http_admin.py::test_admin_shortlist_empty_unsent_batch_returns_batch_id -x` | ❌ W0 rename | ⬜ pending |
| 12-02-01 | 02 | 2 | FIX-01 | T-12-04 | Lock doc both shapes + D-08/D-09 + both D-05 names | docs | `rg -n "test_admin_shortlist_no_batches_returns_null_batch_id\|test_admin_shortlist_empty_unsent_batch_returns_batch_id\|extra=.forbid\|week_start.isoformat" .planning/phases/12-admin-shortlist-empty-batch-contract/12-FIX-01-LOCK.md` | ❌ W0 | ⬜ pending |
| 12-02-02 | 02 | 2 | FIX-01 | T-12-05 | REQUIREMENTS/ROADMAP/PROJECT cite both D-05 proof names | docs | `rg -n "test_admin_shortlist_no_batches_returns_null_batch_id\|test_admin_shortlist_empty_unsent_batch_returns_batch_id" .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/PROJECT.md` | ❌ W0 | ⬜ pending |
| 12-03-01 | 03 | 2 | FIX-01 | T-12-06 / T-12-07 | emptyUnsentDto + EMPTY_UNSENT branch + reset clear | docs/static | `rg -n "emptyUnsentDto\|__DIGEST_ADMIN_EMPTY_UNSENT__" web/src/services/adminApi.js` | ❌ W0 | ⬜ pending |
| 12-03-02 | 03 | 2 | FIX-01 | T-12-06 / T-12-07 | Playwright empty-unsent mirrors D-80; digest_rest absent | e2e | `npm run test:web -- tests/admin.spec.js -g "EMPTY_UNSENT\|empty unsent\|empty-unsent"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Rename `test_admin_shortlist_empty_batch_returns_200_empty_items` → `test_admin_shortlist_no_batches_returns_null_batch_id` (required-key asserts)
- [ ] Add `test_admin_shortlist_empty_unsent_batch_returns_batch_id` in `tests/unit/test_http_admin.py`
- [ ] Add `emptyUnsentDto` + `__DIGEST_ADMIN_EMPTY_UNSENT__` + reset clear in `web/src/services/adminApi.js`
- [ ] Add Playwright empty-unsent case in `tests/admin.spec.js`
- [ ] Create `12-FIX-01-LOCK.md` with both shapes + assert rules
- [ ] Update `.planning/REQUIREMENTS.md` FIX-01 and `.planning/ROADMAP.md` Phase 12 success criteria proof names

*Existing infrastructure covers runners/fixtures — gaps are phase-specific tests/docs only.*

---

## Manual-Only Verifications

All phase behaviors have automated verification (unit + Playwright + lock-doc presence).

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s for unit pair
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
