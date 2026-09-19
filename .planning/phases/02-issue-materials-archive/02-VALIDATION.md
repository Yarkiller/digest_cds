---
phase: 2
slug: issue-materials-archive
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-19
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Playwright `^1.62.1` + pytest via `uv run pytest` |
| **Config file** | `playwright.config.js`; pytest via project `uv` |
| **Quick run command** | `npm run test:web` / `uv run pytest tests/unit/test_http_issues.py -x` |
| **Full suite command** | `npm test` && `npm run test:unit` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** Run targeted pytest file or single Playwright test
- **After every plan wave:** Run `npm run test:web` + `npm run test:unit`
- **Before `/gsd-verify-work`:** Full suite must be green (`npm test` + `npm run test:unit`)
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------------|-----------------|-----------|-------------------|-------------|--------|
| 02-00-01 | 00 | 0 | ISSUE-01 | — | N/A | unit | `uv run pytest tests/unit/test_get_current_issue.py -x` | ❌ W0 | ⬜ pending |
| 02-00-02 | 00 | 0 | ISSUE-04 | — | N/A | unit | `uv run pytest tests/unit/test_list_archive_issues.py -x` | ❌ W0 | ⬜ pending |
| 02-00-03 | 00 | 0 | MAT-01 | — | draft → not found | unit | `uv run pytest tests/unit/test_get_material_for_reader.py -x` | ❌ W0 | ⬜ pending |
| 02-00-04 | 00 | 0 | API | T-02-01 | JWT + 401/404 | unit | `uv run pytest tests/unit/test_http_issues.py tests/unit/test_http_materials.py -x` | ❌ W0 | ⬜ pending |
| 02-W0-e2e | 00 | 0 | ISSUE-01..04, MAT-01..03, PLAT-07 | T-02-02 | soft 404; no mock fallback | e2e | `npx playwright test tests/web-app.spec.js` | ✅ partial | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Planner must expand this map with concrete task IDs when PLAN.md files are written.

---

## Wave 0 Requirements

- [ ] `tests/unit/test_get_current_issue.py` — D-24 selection + empty current
- [ ] `tests/unit/test_list_archive_issues.py` — excludes current
- [ ] `tests/unit/test_get_material_for_reader.py` — draft → not found; ready by slug
- [ ] `tests/unit/test_http_issues.py` / `test_http_materials.py` — JWT + 401/404 shapes
- [ ] Extend `tests/web-app.spec.js` — archive nav, empty states, closed callout, markdown TOC, load-failure splash
- [ ] In-memory fakes for `IssueRepository` / cycle reader in `tests_support/in_memory.py`
- [ ] Optional: unit test for `markdownToc` heading extraction

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Typography-only hero atmosphere | ISSUE-01 / UI-SPEC | Visual density/contrast judgment | Open `/` at 1280 and 390; confirm no cover image, typography-only hero |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
