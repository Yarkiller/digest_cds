---
status: diagnosed
phase: 05-admin-digest-publish
source: [05-VERIFICATION.md]
started: 2026-09-21T18:57:33Z
updated: 2026-09-21T18:10:00Z
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
  truth: "Intro text appears in the letter preview; issue blocks show selected topics as reorderable blocks; optional editor text blocks can sit between articles"
  status: failed
  reason: "User reported: Вводный текст не добавляется в превью письма. Схема дайджеста -> Блоки выпуска Должны отображать выбранные темы кратко (как блоки, положение которых можно менять, устанавливая порядок выхода материала) Также нужна возможность добавлять текстовые блоки редактора между статьсями, чтобы был связующий статьи тект (Но может и отсутствовать)"
  severity: major
  test: 1
  root_cause: "contextText is dead local state and never reaches previewEmail or the preview modal; preview_digest_email builds a title-only body. Issue blocks and interstitial text were never implemented: schemaText is an inert textarea and publication order stays shortlist rank."
  artifacts:
    - path: "web/src/pages/AdminDigestPage.jsx"
      issue: "Editors are not passed to preview; modal renders subject + items and ignores preview.body; schema is a blank textarea"
    - path: "web/src/services/adminApi.js"
      issue: "previewEmail and sendDigest accept no intro or schema payload"
    - path: "backend/src/backend/application/use_cases/preview_digest_email.py"
      issue: "Preview DTO is approved-ready titles only"
  missing:
    - "Include session intro text in the letter preview"
    - "Render selected topics as reorderable issue blocks that set publication order"
    - "Allow optional editor text blocks between articles and compose them into the preview"
  debug_session: ".planning/debug/digest-preview-blocks-intro.md"
- gap_id: G-05-2
  truth: "After send is recorded, used materials and inactive checkboxes are hidden until new materials appear, with «дайджест успешно выпущен» and «Следующие материалы будут подготовлены через X дней»"
  status: failed
  reason: "User reported: pass. Замечание - материалы для выбора после того как отправка записана необходимо скрывать до появления новыйх материалов. Материалы из которых уже были отобраны годные больше не нужно демонстрировать - непонтно зачем, чекбоксы неактивны, их нужно элегантно скрыть, оставив надипись - дайджест успешно выпущен. Следующие материалы будут подготовлены через X дней ."
  severity: minor
  test: 2
  root_cause: "Phase-5 success UX only sets batchSent and «Отправка записана»; confirmSend never clears items, so the shortlist stays mounted. Hide-until-new-batch, the success rest copy, and a days-until-next cadence were never specified and have no API source for X."
  artifacts:
    - path: "web/src/pages/AdminDigestPage.jsx"
      issue: "Post-send path leaves the triage shortlist mounted"
    - path: ".planning/phases/05-admin-digest-publish/05-UI-SPEC.md"
      issue: "Contract has no post-send rest state or countdown copy"
  missing:
    - "Hide the shortlist after a recorded send until a new unsent batch exists"
    - "Show «дайджест успешно выпущен» and «Следующие материалы будут подготовлены через X дней»"
    - "Choose an explicit source for X days; none exists on the shortlist API today"
  debug_session: ".planning/debug/post-send-hide-shortlist.md"