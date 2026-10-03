---
status: partial
phase: 14-draft-ready-justification-honesty
source: [14-VERIFICATION.md]
started: 2026-10-03T17:25:00Z
updated: 2026-10-03T18:12:00Z
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
  reason: "User reported: Кнопка \"Сделать ready\" не срабатывает — toast «Не удалось сделать ready», row stays «черновик» (live mode, VITE_USE_MOCKS=false, real data). Дополнение: «Видимо в базе тоже ничего не меняется» — материал в БД не переходит в ready. Backend-подтверждение (test 5): POST /admin/materials/{id}/ready → HTTP 503 без DevTools-блокировки; initiator adminApi.js:381 — FE корректен, падает бэкенд (вероятно необработанное исключение)."
  severity: blocker
  test: 1
  artifacts: []
  missing:
    - "Inspect backend logs for the /ready route (request_id, traceback) — route may be missing or raising"
    - "Fix the backend exception causing 503 on POST /admin/materials/{id}/ready so the draft→ready write persists"
- gap_id: G-14-2
  truth: "Footer shows only the count-only hint; batch promote «Сделать ready все одобренные черновики (N)» is removed (functionality + display) and the approved-drafts blocker hint is dropped"
  status: failed
  reason: "User reported: Сделать ready все одобренные черновики (2) - убери этот функционал и отображение; подсказку «Уберите черновики из одобренных или дождитесь ready» тоже убрать"
  severity: major
  test: 2
  artifacts: []
  missing:
    - "Remove the batch CTA button (data-testid=admin-mark-ready-batch) and its promoteApprovedDrafts handler/display"
    - "Remove the approved-drafts blocker hint copy «Уберите черновики из одобренных или дождитесь ready» from admin-send-hint"
    - "Update/remove the batch-related Playwright assertions (quantified CTA label, batch markReadyBatch call) that now contradict the removed control"
- gap_id: G-14-3
  truth: "Interactive admin controls show a pointer cursor on hover"
  status: failed
  reason: "User reported (observed while testing 4): «курсор по-прежнему не изменяется при наведении на кнопку Превью материала»"
  severity: cosmetic
  test: 4
  note: "Incidental finding — separate cosmetic defect, not part of test 4's rollback criterion (which passed)"
  artifacts: []
  missing: []
- gap_id: G-14-4
  truth: "Batch promote: ok ids become «готов», failed ids stay «черновик» with a toast listing only the failed ids (D-08 partial success)"
  status: failed
  reason: "User reported: Toast «Не удалось сделать ready: 9, 10, 11, 12» — all 4 failed, not only the one blocked id. The block rule on */admin/materials/12/ready matched 0 requests (batch posts to /admin/materials/ready with no per-id URL), so the partial path could not be exercised."
  severity: major
  test: 5
  note: "Likely shares the live-mode promote failure root cause with G-14-1 (all ids fail). Also mooted if G-14-2 removes the batch control — reconcile at fix planning."
  artifacts: []
  missing: []

## Deferred Follow-Ups

- test: 1
  idea: "UX (для Phase 15+): две операции на одно editorial-решение избыточны для single-operator workflow — объединить Approve (decision) + Mark ready (material_status) в одну кнопку «Одобрить и подготовить → ready»; переименовать «Сделать ready» → «Отобрать», ready → «Отобран»."
  deferred_at: 2026-10-03
