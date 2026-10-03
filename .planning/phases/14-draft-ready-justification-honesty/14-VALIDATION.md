---
phase: "14"
slug: "draft-ready-justification-honesty"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-10-03"
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Per-Task map reconciled to 14-01…03 PLAN task IDs after plan landing.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x (unit) + node:test (FE service) + Playwright 1.x (e2e) |
| **Config file** | root `pyproject.toml` `[tool.pytest.ini_options]`; `playwright.config.js` |
| **Quick run command** | `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_score_factors.py tests/unit/test_http_admin.py -q && node --test tests/unit/test_admin_mark_ready.js` |
| **Full suite command** | `uv run pytest && npm run test:web` |
| **Estimated runtime** | ~60–180 seconds (unit/node gates &lt; 60s; Playwright admin suite within 180s) |

---

## Sampling Rate

- **After every task commit:** Run focused pytest / node --test / Playwright file(s) for the task
- **After every plan wave:** Run `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_score_factors.py tests/unit/test_http_admin.py tests/unit/test_send_digest.py tests/unit/test_set_shortlist_decision.py -q && node --test tests/unit/test_admin_mark_ready.js`
- **Before `/gsd-verify-work`:** Full `uv run pytest` + admin Playwright must be green
- **Max feedback latency:** 180 seconds (prefer node/pytest gates first; Playwright as phase lock)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 14-01-T1 | 14-01 | 1 | ADUX-05 | T-14-01, T-14-02 | Status-only ready; shortlist overlay; D-85 send bridge; no publish | unit/HTTP | `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_http_admin.py -k "ready or draft_in_send_pool" -x` | ❌ W0 | ⬜ pending |
| 14-01-T2 | 14-01 | 1 | ADUX-05 | T-14-01 | Already-ready 200 no-op; employee 403 | unit/HTTP | `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_http_admin.py -k "ready" -x` | ❌ W0 | ⬜ pending |
| 14-02-T1 | 14-02 | 2 | ADUX-05 | T-14-04, T-14-05 | Batch partial success; extra=forbid; employee 403 | unit/HTTP | `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_http_admin.py -k "ready" -x` | ❌ W0 | ⬜ pending |
| 14-02-T2 | 14-02 | 2 | ADUX-05 | T-14-02 | Approve does not auto-ready (D-02) | unit | `uv run pytest tests/unit/test_set_shortlist_decision.py tests/unit/test_http_admin.py -k "approve or decision or draft" -x` | ⚠️ extend | ⬜ pending |
| 14-03-T1 | 14-03 | 3 | ADUX-05 | T-14-09 | markReady/markReadyBatch mocks; batch single-call; empty factor_labels seed | unit (node) | `node --test tests/unit/test_admin_mark_ready.js` | ❌ W0 | ⬜ pending |
| 14-03-T2 | 14-03 | 3 | ADUX-05 | T-14-08, T-14-09 | Per-row + batch UI; optimistic UX; one markReadyBatch | unit+e2e | `node --test tests/unit/test_admin_mark_ready.js && npm run test:web -- tests/admin.spec.js -g "ready\|Сделать ready\|draft hint\|approved draft\|mark-ready-batch\|markReadyBatch"` | ❌ W0 | ⬜ pending |
| 14-03-T3 | 14-03 | 3 | ADUX-06 | T-14-07 | Exact D-15 empty copy; honest_factor_labels 0/1/2+/whitespace | unit+e2e | `uv run pytest tests/unit/test_score_factors.py -x && npm run test:web -- tests/admin.spec.js -g "Обоснование\|обоснование"` | ⚠️ update | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · Task IDs match PLAN.md tasks (14-{plan}-T{n})*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_mark_material_ready.py` — ADUX-05 domain/use-case (status-only, idempotent, not-found, `published_at` unchanged)
- [ ] HTTP cases in `tests/unit/test_http_admin.py` — single + batch ready routes
- [ ] In-memory shortlist↔materials status sync for HTTP/send bridge tests
- [ ] `tests/unit/test_admin_mark_ready.js` + `web/src/services/adminReadyMock.js` — fast FE service gate (batch single-call + material 104 empty `factor_labels`)
- [ ] Playwright: per-row promote + D-85 unblock; batch confirm → one `markReadyBatch`; exact D-15 empty copy (replace old assert)
- [ ] Extend `tests/unit/test_score_factors.py` named matrix cases for D-14 if gaps remain after review

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Soft-warn dialog microcopy for empty body on promote | ADUX-05 (D-10) | Copy is Claude’s discretion; not a product lock string | Promote a draft with empty body; confirm soft «продолжить?» interstitial appears once |

*Automated coverage owns status flip + honesty strings. Manual is microcopy only.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (stubs land during execute)
- [x] No watch-mode flags
- [x] Feedback latency &lt; 180s (node/pytest first; Playwright phase locks)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending (maps reconciled; Wave 0 files still absent until execute)
