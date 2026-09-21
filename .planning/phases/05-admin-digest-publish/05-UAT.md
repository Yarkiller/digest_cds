---
status: testing
phase: 05-admin-digest-publish
source: [05-VERIFICATION.md]
started: 2026-09-21T18:57:33Z
updated: 2026-09-21T18:57:33Z
---

## Current Test

number: 1
name: Live admin shortlist + employee ForbiddenPage
expected: |
  Log in as profiles.role=admin on live stack; open /admin/digest.
  ≤5 ranked rows with draft/ready + score/factors or «обоснование недоступно»;
  employee deep-link shows ForbiddenPage.
awaiting: user response

## Tests

### 1. Live admin shortlist + employee ForbiddenPage
expected: ≤5 ranked rows with draft/ready + score/factors or «обоснование недоступно»; employee deep-link shows ForbiddenPage
result: [pending]

### 2. Live preview + stub send
expected: «Отправка записана», archive issue appears, send locks as already-sent; approved draft blocks send
result: [pending]

### 3. ADMIN-08 returnUrl after login
expected: sanitizeReturnUrl keeps same-origin path; lands on published issue after login via /issues/{n}
result: [pending]

### 4. Acknowledge 05-REVIEW CR-01 risk
expected: Accept stuck sent_at if publish fails post-claim, or schedule RPC/compensation follow-up
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
