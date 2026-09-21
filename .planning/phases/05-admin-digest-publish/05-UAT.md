---
status: complete
phase: 05-admin-digest-publish
source: [05-VERIFICATION.md]
started: 2026-09-21T18:57:33Z
updated: 2026-09-21T17:44:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Live admin shortlist + employee ForbiddenPage
expected: ≤5 ranked rows with draft/ready + score/factors or «обоснование недоступно»; employee deep-link shows ForbiddenPage
result: issue
reported: "Вводный текст не добавляется в превью письма. Схема дайджеста -> Блоки выпуска Должны отображать выбранные темы кратко (как блоки, положение которых можно менять, устанавливая порядок выхода материала) Также нужна возможность добавлять текстовые блоки редактора между статьсями, чтобы был связующий статьи тект (Но может и отсутствовать)"
severity: major

### 2. Live preview + stub send
expected: «Отправка записана», archive issue appears, send locks as already-sent; approved draft blocks send
result: issue
reported: "pass. Замечание - материалы для выбора после того как отправка записана необходимо скрывать до появления новыйх материалов. Материалы из которых уже были отобраны годные больше не нужно демонстрировать - непонтно зачем, чекбоксы неактивны, их нужно элегантно скрыть, оставив надипись - дайджест успешно выпущен. Следующие материалы будут подготовлены через X дней ."
severity: minor

### 3. ADMIN-08 returnUrl after login
expected: sanitizeReturnUrl keeps same-origin path; lands on published issue after login via /issues/{n}
result: pass

### 4. Acknowledge 05-REVIEW CR-01 risk
expected: Accept stuck sent_at if publish fails post-claim, or schedule RPC/compensation follow-up
result: pass

## Summary

total: 4
passed: 2
issues: 2
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-05-1
  truth: "≤5 ranked rows with draft/ready + score/factors or «обоснование недоступно»; employee deep-link shows ForbiddenPage"
  status: failed
  reason: "User reported: Вводный текст не добавляется в превью письма. Схема дайджеста -> Блоки выпуска Должны отображать выбранные темы кратко (как блоки, положение которых можно менять, устанавливая порядок выхода материала) Также нужна возможность добавлять текстовые блоки редактора между статьсями, чтобы был связующий статьи тект (Но может и отсутствовать)"
  severity: major
  test: 1
  artifacts: []
  missing: []
- gap_id: G-05-2
  truth: "«Отправка записана», archive issue appears, send locks as already-sent; approved draft blocks send"
  status: failed
  reason: "User reported: pass. Замечание - материалы для выбора после того как отправка записана необходимо скрывать до появления новыйх материалов. Материалы из которых уже были отобраны годные больше не нужно демонстрировать - непонтно зачем, чекбоксы неактивны, их нужно элегантно скрыть, оставив надипись - дайджест успешно выпущен. Следующие материалы будут подготовлены через X дней ."
  severity: minor
  test: 2
  artifacts: []
  missing: []