---
status: diagnosed
phase: 14-draft-ready-justification-honesty
source: [14-VERIFICATION.md]
started: 2026-10-03T17:25:00Z
updated: 2026-10-03T18:20:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Long title + ready CTA layout
expected: Title wraps with break-words; draft badge and «Сделать ready» remain clickable without overflow clipping
result: issue
reported: "Кнопка \"Сделать ready\" не срабатывает. (живой режим, реальные данные) — по клику показывается тост «Не удалось сделать ready», строка остаётся «черновик»"
severity: blocker

### 2. Sticky footer with many approved drafts
expected: With N≥2 approved drafts, the count-only hint and «Сделать ready все одобренные черновики (N)» CTA remain visible and hit-testable without covering each other (footer no longer re-lists titles — 14-05 / G-14-2b)
result: issue
reported: "Сделать ready все одобренные черновики (2) - убери этот функционал и отображение. Уберите черновики из одобренных или дождитесь ready. — тоже убрать"
severity: major

### 3. Factor caption / empty justification wrap
expected: Long captions and the D-15 empty sentence wrap with break-words inside max-w-[12rem] without breaking the shortlist row grid
result: pass

### 4. Per-row promote failure rollback (D-05)
expected: A toast is shown and the row rolls back to «черновик» (no fake ready)
why_human: Rollback-on-failure state transition; no failure-injection exists for markReady and no test exercises the promote-failure branch — happy path only is Playwright-covered
result: pass
note: "Роллбэк подтверждён на живых данных: тост «Не удалось сделать ready», бейдж остался «черновик». Отдельно замечено: курсор не меняется при наведении на «Превью материала» (см. G-14-3)."

### 5. Batch partial-failure rollback (D-08)
expected: ok ids become «готов»; failed ids stay «черновик» with a toast listing them
why_human: Rollback of failed ids is a state transition; the batch Playwright case exercises only the all-ok path
result: issue
reported: "Test 5: fail — backend 503. POST /admin/materials/{id}/ready → 503 (Service Unavailable), воспроизводится без блокировки DevTools (подтверждено). Initiator adminApi.js:381 — FE корректна; падает бэкенд (вероятно необработанное исключение)."
severity: major

### 6. Batch stale-refetch no-clobber (G-14-2 batch half / 14-REVIEW WR-03)
expected: Promoted ok ids stay «готов» after a stale batch refetch (backend acks but the shortlist still reports draft)
why_human: The __DIGEST_ADMIN_STALE_READY__ harness is honoured only by the single markReady mock; the batch preservePromotedReady call is asserted only by a source-text regex
result: blocked
blocked_by: other
reason: "Not proceeding — depends on a working promote (blocked by the live backend 503 on POST /admin/materials/{id}/ready, G-14-1/G-14-4). Re-test after the promote backend failure is fixed."

## Summary

total: 6
passed: 2
issues: 3
pending: 0
skipped: 0
blocked: 1

## Gaps

<!-- YAML format for plan-phase --gaps consumption -->
- gap_id: G-14-1
  truth: "Draft badge and «Сделать ready» remain usable: clicking per-row «Сделать ready» promotes the draft to ready"
  status: failed
  reason: "User reported: Кнопка \"Сделать ready\" не срабатывает — toast «Не удалось сделать ready», row stays «черновик» (live mode). Log: POST /admin/materials/{id}/ready → 503."
  severity: blocker
  test: 1
  root_cause: "SupabaseMaterialRepository._fetch_one embeds `material_relations(to_material_id)` without disambiguating the FK; materials↔material_relations has two FKs (from_material_id / to_material_id), so PostgREST returns PGRST201 (ambiguous embed), the driver raises APIError, and _fetch_one wraps it in PersistenceError — every live repo.get()/get_by_slug() fails. mark_material_ready → repo.get() → PersistenceError → route maps to 503."
  artifacts:
    - path: "supabase-integration/src/supabase_integration/material_repository.py"
      issue: "Ambiguous `material_relations(to_material_id)` embed in _fetch_one (line ~135); must be disambiguated by FK name. Also verify the `material_tags(...)` embed resolves unambiguously."
    - path: "backend/src/backend/application/use_cases/mark_material_ready.py"
      issue: "Surfaces the PersistenceError from repo.get() (no masking)"
    - path: "backend/src/backend/interface/http/routes/admin.py"
      issue: "Maps PersistenceError → 503 materials_unavailable (line ~293)"
  missing:
    - "Disambiguate the embed in _fetch_one to `material_relations!material_relations_from_material_id_fkey(to_material_id)` (and confirm material_tags is unambiguous)"
    - "Add a regression test that fails on the ambiguous embed / PGRST201 class (fake-client or contract) — the existing fake/InMemory repos never hit the real PostgREST embed"
    - "Re-run the live read probe to confirm get()/get_by_slug() return a Material (also unblocks the public reader)"
  debug_session: .planning/debug/mark-ready-503.md
- gap_id: G-14-2
  truth: "Footer no longer offers a batch promote: «Сделать ready все одобренные черновики (N)» and the «Уберите черновики из одобренных или дождитесь ready» hint are removed (display + functionality)"
  status: failed
  reason: "User reported: Сделать ready все одобренные черновики (2) - убери этот функционал и отображение; подсказку «Уберите черновики из одобренных или дождитесь ready» тоже убрать"
  severity: major
  test: 2
  root_cause: "Intentional product change (operator decision), not a defect: the batch CTA and the approved-drafts hint are to be removed. Per-row «Сделать ready» stays."
  artifacts:
    - path: "web/src/pages/AdminDigestPage.jsx"
      issue: "Batch CTA render (lines ~837-847, data-testid=admin-mark-ready-batch), promoteApprovedDrafts handler (~374), and sendHint draft branch (~255-257) all present"
    - path: "web/src/services/adminApi.js"
      issue: "markReadyBatch becomes unused once the CTA is removed"
    - path: "tests/admin.spec.js"
      issue: "Asserts the quantified batch CTA, the one-batch-call counter, and the draft hint"
    - path: "tests/unit/test_admin_mark_ready.js"
      issue: "Asserts the batch helper single-call shape"
  missing:
    - "Remove the batch CTA button and its promoteApprovedDrafts handler/display"
    - "Remove the approved-drafts hint copy «Уберите черновики из одобренных или дождитесь ready.» and make sendHint fall through coherently when approvedDrafts.length > 0 (keep the sendUnlocked gate requiring approvedDrafts.length === 0 for D-85)"
    - "Update/remove the contradicting batch Playwright + node assertions; decide whether the now-unused FE markReadyBatch and backend batch route/mark_materials_ready are deleted or unhooked"
  debug_session: .planning/debug/admin-batch-cta-removal.md
- gap_id: G-14-3
  truth: "Interactive admin controls show a pointer cursor on hover (incl. «Превью материала»)"
  status: failed
  reason: "User reported (observed while testing 4): «курсор по-прежнему не изменяется при наведении на кнопку Превью материала»"
  severity: cosmetic
  test: 4
  note: "Incidental finding — separate cosmetic defect, not part of test 4's rollback criterion (which passed)"
  root_cause: "The «Превью материала» button has no cursor-pointer class and web/src/index.css defines no global <button> cursor rule, so the browser shows the default cursor."
  artifacts:
    - path: "web/src/pages/AdminDigestPage.jsx"
      issue: "«Превью материала» button className (lines ~812-819) lacks cursor-pointer"
    - path: "web/src/index.css"
      issue: "No global cursor rule for buttons"
  missing:
    - "Add cursor-pointer to «Превью материала» (and audit other Phase 14 interactive controls for the same omission)"
    - "Regression-lock via Playwright/class assertion (cursor: pointer)"
  debug_session: .planning/debug/preview-cursor.md
- gap_id: G-14-4
  truth: "Batch promote: ok ids become «готов», failed ids stay «черновик» with a toast listing only the failed ids (D-08 partial success)"
  status: failed
  reason: "User reported: Toast «Не удалось сделать ready: 9, 10, 11, 12» — all 4 failed, not only the blocked id. Log confirms POST /admin/materials/ready → 200 with all results ok=false."
  severity: major
  test: 5
  root_cause: "Same as G-14-1: every mark_material_ready raises PersistenceError (ambiguous embed), so the batch returns HTTP 200 with all ids failing (error=materials_unavailable). The 'partial success' path is unreachable while promote is globally broken — not a separate defect."
  note: "Reconcile with G-14-2: removing the batch CTA makes this moot on the FE; fix it only if the backend batch path is retained. Verify a genuine partial result after the G-14-1 fix."
  artifacts:
    - path: "backend/src/backend/application/use_cases/mark_material_ready.py"
      issue: "mark_materials_ready catches the per-id PersistenceError → ok=false for all ids"
  missing:
    - "Resolved by the G-14-1 fix once a working promote exists; re-test the partial path (or drop the batch path per G-14-2)"
  debug_session: .planning/debug/mark-ready-503.md

## Deferred Follow-Ups

- test: 1
  idea: "UX (для Phase 15+): две операции на одно editorial-решение избыточны для single-operator workflow — объединить Approve (decision) + Mark ready (material_status) в одну кнопку «Одобрить и подготовить → ready»; переименовать «Сделать ready» → «Отобрать», ready → «Отобран»."
  deferred_at: 2026-10-03
