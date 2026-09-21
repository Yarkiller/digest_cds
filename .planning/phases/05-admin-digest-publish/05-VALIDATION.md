---
phase: 5
slug: admin-digest-publish
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-21
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (≥8.3) + Playwright (@playwright/test ^1.62.1) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`; Playwright via `package.json` scripts |
| **Quick run command** | `uv run pytest tests/unit/test_http_admin.py -x` |
| **Full suite command** | `uv run pytest` && `npm run test:web` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** Run targeted unit file(s) for the behavior (`-x`)
- **After every plan wave:** Run `uv run pytest` + affected Playwright project
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-W0-me | 00 | 0 | D-76 | T-05-spoof | `/me.role` is app_role | unit | `uv run pytest tests/unit/test_http_me.py -x` | ✅ exists | ⬜ pending |
| 05-01-shortlist | 01 | 1 | ADMIN-01 | — | Admin GET ≤5; empty honesty | unit HTTP | `uv run pytest tests/unit/test_http_admin.py -k shortlist -x` | ❌ W0 | ⬜ pending |
| 05-01-403-api | 01 | 1 | AUTH-03 | T-05-eop | Non-admin → 403 API | unit HTTP | `uv run pytest tests/unit/test_http_admin.py -k forbidden -x` | ❌ W0 | ⬜ pending |
| 05-01-403-ui | 01 | 1 | AUTH-03 | T-05-eop | Employee deep-link → 403 page | e2e | `npx playwright test tests/admin.spec.js -g "403"` | ❌ W0 | ⬜ pending |
| 05-02-decision | 02 | 2 | ADMIN-02 | — | Approve/Reject persists | unit | `uv run pytest tests/unit/test_set_shortlist_decision.py -x` | ❌ W0 | ⬜ pending |
| 05-03-draft-block | 03 | 2 | ADMIN-03 | T-05-draft | Send blocked on approved draft | unit | `uv run pytest tests/unit/test_send_digest.py -k draft -x` | ❌ W0 | ⬜ pending |
| 05-04-preview | 04 | 2 | ADMIN-04 | — | Preview match; fail ≠ verified | unit | `uv run pytest tests/unit/test_preview_digest.py -x` | ❌ W0 | ⬜ pending |
| 05-05-factors | 02 | 2 | ADMIN-05 | — | Factors ≥2 or недоступно | unit | `uv run pytest tests/unit/test_score_factors.py -x` | ❌ W0 | ⬜ pending |
| 05-06-batch | 05 | 3 | ADMIN-06 | — | Select-all / top-N checkboxes | e2e | `npx playwright test tests/admin.spec.js -g "топ"` | ❌ W0 | ⬜ pending |
| 05-07-send | 03 | 2 | ADMIN-07 | T-05-double | Send success; repeat 409 | unit | `uv run pytest tests/unit/test_send_digest.py -x` | ❌ W0 | ⬜ pending |
| 05-08-link | 03 | 2 | ADMIN-08 | T-05-redirect | Stub body `/issues/{n}` + returnUrl | unit | `uv run pytest tests/unit/test_stub_mailer.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Align `InMemoryProfileRepository` + `meApi` mocks + `test_http_me` to `app_role` (`employee` default)
- [ ] `tests/unit/test_http_admin.py` — 403 matrix for all admin routes
- [ ] `tests/unit/test_send_digest.py` / `test_preview_digest.py` / `test_set_shortlist_decision.py`
- [ ] `tests/admin.spec.js` — 403 page, empty state, draft block, preview gate, select-all/top-N (mocks)
- [ ] Migration `005_phase5_admin_shortlist.sql` — delivery columns + seed batch (comment «demo batch для Phase 5»)
- [ ] Runbook **§4e** stub mailer + seed honesty + promote admin profile
- [ ] `require_admin` dependency + empty `routes/admin.py` router registered in `app.py`
- [ ] In-memory `ShortlistRepository` + `StubMailer` fakes in `tests_support`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Promote a live Auth user to `admin` for ops proof | AUTH-03 / runbook | Environment-specific profile row | Follow runbook §4e after migrate; verify `/admin/digest` loads |

*Otherwise: All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
