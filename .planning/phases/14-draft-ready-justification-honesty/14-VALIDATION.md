---
phase: "14"
slug: "draft-ready-justification-honesty"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-03"
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x (unit) + Playwright 1.x (e2e) |
| **Config file** | root `pyproject.toml` `[tool.pytest.ini_options]`; `playwright.config.js` |
| **Quick run command** | `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_score_factors.py tests/unit/test_http_admin.py -q` |
| **Full suite command** | `uv run pytest && npm run test:web` |
| **Estimated runtime** | ~60–180 seconds |

---

## Sampling Rate

- **After every task commit:** Run focused pytest / Playwright file(s) for the task
- **After every plan wave:** Run `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_score_factors.py tests/unit/test_http_admin.py tests/unit/test_send_digest.py tests/unit/test_set_shortlist_decision.py -q`
- **Before `/gsd-verify-work`:** Full `uv run pytest` + admin Playwright must be green
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 14-W0 | 00 | 0 | ADUX-05/06 | — | Wave 0 stubs + in-memory status sync | unit | `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_score_factors.py -q` | ❌ W0 | ⬜ pending |
| 14-ADUX-05-domain | TBD | TBD | ADUX-05 | T-14-01 | Status-only ready; no publish; `published_at` unchanged | unit | `uv run pytest tests/unit/test_mark_material_ready.py -x` | ❌ W0 | ⬜ pending |
| 14-ADUX-05-http | TBD | TBD | ADUX-05 | T-14-01 | Admin-only single + batch ready; `extra=forbid` | unit | `uv run pytest tests/unit/test_http_admin.py -k ready -x` | ❌ W0 | ⬜ pending |
| 14-ADUX-05-send | TBD | TBD | ADUX-05 | T-14-02 | After ready, D-85 `DraftInSendPoolError` clears for that material | unit | `uv run pytest tests/unit/test_send_digest.py -k draft -x` | ⚠️ partial | ⬜ pending |
| 14-ADUX-05-approve | TBD | TBD | ADUX-05 | T-14-02 | Approve does not auto-ready | unit | `uv run pytest tests/unit/test_set_shortlist_decision.py -x` | ⚠️ extend | ⬜ pending |
| 14-ADUX-05-ui | TBD | TBD | ADUX-05 | T-14-01 | Per-row + batch promote; optimistic UX | e2e | `npm run test:web -- tests/admin.spec.js -g "ready"` | ❌ W0 | ⬜ pending |
| 14-ADUX-06-labels | TBD | TBD | ADUX-06 | T-14-03 | `honest_factor_labels` 0/1/2+/whitespace | unit | `uv run pytest tests/unit/test_score_factors.py -x` | ✅ extend | ⬜ pending |
| 14-ADUX-06-empty | TBD | TBD | ADUX-06 | T-14-03 | Exact empty copy `Обоснование недоступно — скоринг не запускался` | e2e | `npm run test:web -- tests/admin.spec.js -g "Обоснование\|обоснование"` | ⚠️ update | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · Task IDs refined when PLAN.md waves land*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_mark_material_ready.py` — ADUX-05 domain/use-case (status-only, idempotent, not-found, `published_at` unchanged)
- [ ] HTTP cases in `tests/unit/test_http_admin.py` — single + batch ready routes
- [ ] In-memory shortlist↔materials status sync for HTTP/send bridge tests
- [ ] Playwright: promote control + D-85 unblock smoke; exact D-15 empty copy (replace old assert)
- [ ] Extend `tests/unit/test_score_factors.py` named matrix cases for D-14 if gaps remain after review

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Soft-warn dialog microcopy for empty body on promote | ADUX-05 (D-10) | Copy is Claude’s discretion; not a product lock string | Promote a draft with empty body; confirm soft «продолжить?» interstitial appears once |

*Automated coverage owns status flip + honesty strings. Manual is microcopy only.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
