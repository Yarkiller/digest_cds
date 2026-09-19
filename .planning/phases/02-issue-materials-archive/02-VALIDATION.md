---
phase: 2
slug: issue-materials-archive
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-19
updated: 2026-09-19
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
| 02-01-01 | 01 | 1 | ISSUE-01 | T-02-01 | JWT on GET /issues/current | unit | `uv run pytest tests/unit/test_get_current_issue.py tests/unit/test_http_issues.py -x` | ❌ | ⬜ pending |
| 02-01-02 | 01 | 1 | ISSUE-01 | T-02-02 | empty CTA no blank page | e2e | `npx playwright test tests/web-app.spec.js -g "готовится\|issue\|выпуск"` | ❌ | ⬜ pending |
| 02-01-03 | 01 | 1 | — | — | Wave 0 scaffolds | unit | scaffolds present; current tests green | ❌ | ⬜ pending |
| 02-02-01 | 02 | 2 | ISSUE-01, MAT-01 | T-02-04 | idempotent seed no TRUNCATE | script | node check on `002_phase2_issue_seed.sql` | ❌ | ⬜ pending |
| 02-02-02 | 02 | 2 | ISSUE-01, MAT-01 | T-02-03, T-02-05 | service_role adapters only | unit | `uv run pytest tests/unit/test_supabase_issue_repository_contract.py tests/unit/test_live_container_wiring.py -x` | ❌ | ⬜ pending |
| 02-02-03 | 02 | 2 | ISSUE-01 | T-02-04 | [BLOCKING] seed applied | human | SQL counts after push/MCP | ❌ | ⬜ pending |
| 02-03-01 | 03 | 3 | ISSUE-04 | T-02-01 | archive excludes current | unit | `uv run pytest tests/unit/test_list_archive_issues.py tests/unit/test_get_issue_by_number.py tests/unit/test_http_issues.py -x` | ❌ | ⬜ pending |
| 02-03-02 | 03 | 3 | ISSUE-04 | — | /archive nav + past issue | e2e | `npx playwright test tests/web-app.spec.js -g "archive\|Архив"` | ❌ | ⬜ pending |
| 02-04-01 | 04 | 4 | MAT-02 | T-02-01 | draft → 404 | unit | `uv run pytest tests/unit/test_get_material_for_reader.py tests/unit/test_http_materials.py -x` | ❌ | ⬜ pending |
| 02-04-02 | 04 | 4 | MAT-01 | T-02-06 | rehype-sanitize TOC | unit | `node --test tests/unit/test_markdown_toc.js` | ❌ | ⬜ pending |
| 02-04-03 | 04 | 4 | MAT-01, MAT-02, MAT-03, ISSUE-03 | T-02-06 | prose + soft 404 + dek hide | e2e | `npx playwright test tests/web-app.spec.js -g "material\|материал\|rag-systems"` | ❌ | ⬜ pending |
| 02-05-01 | 05 | 5 | ISSUE-02 | — | open/closed callout stub | unit | `uv run pytest tests/unit/test_get_current_issue.py tests/unit/test_http_issues.py -x` | ❌ | ⬜ pending |
| 02-05-02 | 05 | 5 | PLAT-07 / D-21 | T-02-02 | splash no mock fallback | e2e | `npx playwright test tests/web-app.spec.js -g "ошибочка\|bad_gateway\|Повторить"` | ❌ | ⬜ pending |
| 02-05-03 | 05 | 5 | ISSUE-01..04, MAT-01..03 | T-02-02 | phase gate | e2e+unit | `npm run test:web && npm run test:unit` | ❌ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_get_current_issue.py` — D-24 selection + empty current (02-01)
- [ ] `tests/unit/test_list_archive_issues.py` — excludes current (scaffold 02-01, green 02-03)
- [ ] `tests/unit/test_get_material_for_reader.py` — draft → not found; ready by slug (scaffold 02-01, green 02-04)
- [ ] `tests/unit/test_http_issues.py` / `test_http_materials.py` — JWT + 401/404 shapes
- [ ] Extend `tests/web-app.spec.js` — archive nav, empty states, closed callout, markdown TOC, load-failure splash (02-05)
- [ ] In-memory fakes for `IssueRepository` / cycle reader in `tests_support/in_memory.py`
- [ ] Optional: unit test for `markdownToc` heading extraction (02-04)

---

## Flagged assumptions (SPECLESS / EDGE_ABSENT)

All ISSUE-*/MAT-* probe items were unclassified; plans author explicit must_haves from CONTEXT/RESEARCH/UI-SPEC:

| Assumption | Source | Plan handling |
|------------|--------|---------------|
| A1 Editor byline constant string | RESEARCH | 02-04 DTO constant — no schema column |
| A2 Open-first else latest closed cycle | RESEARCH | 02-05 use-case selection |
| A3 rehype-sanitize required | RESEARCH security | 02-04 deps + threat T-02-06 |
| A4 Archive cards typography/count only | RESEARCH / UI-SPEC | 02-03 — no thumbs required |
| Unpublished issue number → soft empty | RESEARCH open Q1 | 02-03 404/empty + CTA to current |
| UI-SPEC 10 backstops | 02-UI-SPEC ## UI Considerations | 02-01/03/04/05 must_haves.truths — verify visually at phase verify |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Typography-only hero atmosphere | ISSUE-01 / UI-SPEC | Visual density/contrast judgment | Open `/` at 1280 and 390; confirm no cover image, typography-only hero |
| UI-SPEC backstops (overflow/plural/long-text/nav) | UI Considerations | Held-out visual | Spot-check IssueTOC, archive grid, material TOC, hero, nav at 390/1280 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
