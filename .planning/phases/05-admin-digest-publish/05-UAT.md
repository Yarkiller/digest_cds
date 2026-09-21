---
status: testing
phase: 05-admin-digest-publish
source: [05-VERIFICATION.md]
started: 2026-09-21T18:57:33Z
updated: 2026-09-21T19:23:41Z
---

## Current Test

number: 1
name: Live re-UAT G-05-1 — intro, reorder, interstitial, preview, send
expected: |
  Intro + interstitial appear in preview.body; material titles follow block order; send records «Отправка записана» and archive issue; StubMailer body uses the same material order
awaiting: user response

## Tests

### 1. Live re-UAT G-05-1: as admin, fill «Вводный текст», reorder «Блоки выпуска», insert interstitial text, open «Превью письма», then send
expected: Intro + interstitial appear in preview.body; material titles follow block order; send records «Отправка записана» and archive issue; StubMailer body uses the same material order
result: [pending]

### 2. Live re-UAT G-05-2: after recorded send (and cold reload of /admin/digest)
expected: Shortlist/checkboxes/editors hidden; rest shows «дайджест успешно выпущен» and «через 7 дней»; banners «Отправка записана» / «Уже отправлено» still usable; genuine empty still D-80
result: [pending]

### 3. Acknowledge 05-REVIEW CR-01 (post-05-08): rank rewrite outside RPC
expected: Accept scrambled ranks on a failed send, or schedule an RPC p_material_ids / transactional rewrite follow-up
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

Prior cycle (diagnosed): test 1 major (composition) and test 2 minor (post-send rest) are the gaps closed by 05-07…05-09. Tests 3 (ADMIN-08 returnUrl) and 4 (earlier CR-01 stuck sent_at) passed. This cycle re-tests the closed gaps on the live path and asks for a decision on the new rank-rewrite finding.
