---
phase: 4
slug: knowledge-razbory
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-20
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`uv run pytest`) + Playwright `@playwright/test` ^1.62.1 |
| **Config file** | `playwright.config.js`; pytest via uv project |
| **Quick run command** | `uv run pytest tests/unit/test_search_knowledge.py -x` |
| **Full suite command** | `npm run test:unit && npm run test:web` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** Run targeted pytest file(s) for touched use-case/route
- **After every plan wave:** `npm run test:unit` + affected Playwright project
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** Prefer &lt;60s per task; full suite ~120s allowed at phase gate

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-W0-01 | 00 | 0 | KNOW-01 | T-04-score | Omit score from HTTP; blank q → 400 | unit | `uv run pytest tests/unit/test_http_knowledge_search.py -x` | ❌ W0 | ⬜ pending |
| 04-W0-02 | 00 | 0 | KNOW-02…04 | T-04-draft | Role allowlist; no ML substitute on empty | unit | `uv run pytest tests/unit/test_search_knowledge.py -x` | ⚠️ extend | ⬜ pending |
| 04-W0-03 | 00 | 0 | RAZB-01…04 | T-04-path | JWT; path containment for notebooks | unit | `uv run pytest tests/unit/test_http_razbory.py -x` | ❌ W0 | ⬜ pending |
| 04-W0-04 | 00 | 0 | KNOW/RAZB | — | Submit/Enter, chips, TOC, notebook UX | e2e | Playwright knowledge + razbory specs | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement → assertion path (phase gate)

| Requirement | Automated path |
|-------------|----------------|
| KNOW-01 | unit search/HTTP blank-400 + honest empty; e2e Submit/Enter; whitespace does not search |
| KNOW-02 | unit role_filter analyst; e2e Analyst chip |
| KNOW-03 | e2e DS search → open material |
| KNOW-04 | unit empty honesty; e2e «Сбросить фильтр» clears role only |
| RAZB-01 | unit HTTP list; e2e empty CTA → `/voting` |
| RAZB-02 | e2e sticky TOC section jump |
| RAZB-03 | unit FileResponse; e2e enabled/disabled + «Notebook скоро будет» |
| RAZB-04 | unit DTO content_kind; e2e «Качество» vs «Обзор» |

---

## Wave 0 Requirements

- [ ] `tests/unit/test_http_knowledge_search.py` — KNOW-01…04 HTTP contract (blank 400, role filter, no score field, pagination)
- [ ] Extend `tests/unit/test_search_knowledge.py` — role filter empty honesty; material dedupe; offset
- [ ] `tests/unit/test_http_razbory.py` — list/detail/announcement/404/notebook
- [ ] `tests/unit/test_razbor_use_cases.py` — content_kind metrics vs overview
- [ ] Rewrite `tests/web-app.spec.js` knowledge cases (remove tag facet; add Submit/Enter, chips, reset-filter-only)
- [ ] New Playwright razbory specs (list empty CTA, sticky TOC, notebook disabled/enabled, Обзор vs Качество)
- [ ] In-memory `RazborRepository` + `QueryEmbedder` fakes in `tests_support`
- [ ] Seed fixtures: chunks+embeddings, published multi-section razbor ± notebook, announcement, overview-without-metrics

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Snippet row + no numeric scores | KNOW-01 / D-59 | Visual ranking honesty | Search at 1280; confirm snippet rows, no score badges |
| Chronology list vs material cards | RAZB-01 / D-67 | Layout judgment | Open `/razbory`; confirm date/status overline pattern |
| Dual notebook strip placement | RAZB-03 / D-71 | Layout | Published razbor with notebook — strip at top and near end |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s (task) / ~120s (phase gate)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
