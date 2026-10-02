---
phase: "13"
slug: "admin-material-email-preview-honesty"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-02"
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (unit) + Playwright (e2e) |
| **Config file** | root `pyproject.toml` `[tool.pytest.ini_options]`; `playwright.config.js` |
| **Quick run command** | `uv run pytest tests/unit/test_email_render.py tests/unit/test_http_admin.py -x` |
| **Full suite command** | `npm run test:unit && npm run test:web` |
| **Estimated runtime** | ~60–180 seconds |

---

## Sampling Rate

- **After every task commit:** Run focused pytest file(s) for the task
- **After every plan wave:** Run `npm run test:unit`
- **Before `/gsd-verify-work`:** `npm run test:unit && npm run test:web` must be green
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-W0-01 | 00 | 0 | ADUX-01 | T-13-01 | Admin-only shortlist enrichment | unit | `uv run pytest tests/unit/test_http_admin.py::test_admin_shortlist_returns_full_items -x` | ❌ W0 | ⬜ pending |
| 13-W0-02 | 00 | 0 | ADUX-02 | T-13-02 | Escaped HTML in preview DTO | unit | `uv run pytest tests/unit/test_preview_digest.py -k html -x` | ❌ W0 | ⬜ pending |
| 13-W0-03 | 00 | 0 | ADUX-02 | T-13-02 | preview html == send html | unit | `uv run pytest -k test_preview_email_html_matches_send_html -x` | ❌ W0 | ⬜ pending |
| 13-W0-04 | 00 | 0 | ADUX-03 | T-13-02 | Interstitial `\n\n` → paragraphs | unit | `uv run pytest tests/unit/test_email_render.py -x` | ❌ W0 | ⬜ pending |
| 13-W0-05 | 00 | 0 | ADUX-04 | T-13-03 | Ban-list asserts; no runtime strip | unit | `uv run pytest -k test_header -x` | ❌ W0 | ⬜ pending |
| 13-W0-06 | 00 | 0 | ADUX-01/02 | T-13-02 | iframe + material modal e2e | e2e | `npx playwright test tests/admin.spec.js -g "material preview\|email preview"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_email_render.py` — interstitial matrix + `render_email_html` + ban asserts (ADUX-02/03/04)
- [ ] `tests/unit/test_http_admin.py::test_admin_shortlist_returns_full_items` — ADUX-01
- [ ] `tests/unit/test_preview_digest.py` / send tests — html field + parity
- [ ] Update `tests/admin.spec.js` email preview selectors for iframe
- [ ] Extend FE mocks in `web/src/services/adminApi.js` with full item fields + `html`
- [ ] Update `12-FIX-01-LOCK.md` item schema section (D-03)
- [ ] Migration `010_phase13_scrub_test_header.sql` + runbook §4f
- [ ] In-memory shortlist seeds must carry new `ShortlistItem` fields

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual paragraph spacing in email iframe | ADUX-03 | Pixel spacing subjective | Open «Превью письма»; confirm `\n\n` interstitial shows as separate paragraphs |

*Automated unit matrix covers `\n\n` → `<p>`; manual is polish-only.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
