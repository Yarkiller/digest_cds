---
status: complete
phase: 01-platform-foundation-auth
source:
  - 01-01-SUMMARY.md
  - 01-02-SUMMARY.md
  - 01-03-SUMMARY.md
  - 01-04-SUMMARY.md
  - 01-05-SUMMARY.md
  - 01-06-SUMMARY.md
started: 2026-09-19T18:50:00Z
updated: 2026-09-19T19:10:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running Vite/uvicorn. Start from scratch per docs/agents/local-platform-runbook.md: FastAPI (APP_CONTAINER=live) and Vite (VITE_USE_MOCKS=false) boot without errors; GET /health returns live JSON; SPA loads login or issue without crash.
result: pass

### 2. Manual corporate Auth users on shared Supabase dashboard
expected: 1–2 corporate test users (@sberbank.ru / @omega.sbrf.ru) exist in the shared Supabase Auth dashboard and can sign in (D-08; not automated against shared VM).
result: pass
rationale: D-08 forbids automated seed against shared VM; deferred to Plan 01-06 live proof
reason: human_judgment
coverage_id: 01-04-D5

### 3. Live FE↔BE proof: corporate login → GET /me → POST /me/ping → activity_events
expected: With VITE_USE_MOCKS=false and live API, corporate login lands on issue; PlatformProofBanner shows identity from GET /me; Ping succeeds and a platform_ping row appears in activity_events.
result: issue
reported: "кнопка Регистрация не активна и не ведёт к регистрации. Форма для входа не должна иметь поля Имя (при каждом входе заполнять нельзя). Форма регистрации должна иметь поле имени с понятной подписью — например ФИО или только Имя."
severity: major
rationale: Blocking-human checkpoint; operator may re-confirm after stale verification.
reason: human_judgment
coverage_id: 01-06-D3

### 4. GET /health returns 200 JSON status ok without auth
expected: GET /health returns 200 JSON status ok without auth
result: pass
source: automated
coverage_id: 01-01-D1

### 5. CORS allowlist from API_CORS_ORIGINS reflects allowed Origin
expected: CORS allowlist from API_CORS_ORIGINS reflects allowed Origin
result: pass
source: automated
coverage_id: 01-01-D2

### 6. X-Request-ID on responses; structlog JSON includes bound request_id
expected: X-Request-ID on responses; structlog JSON includes bound request_id
result: pass
source: automated
coverage_id: 01-01-D3

### 7. Committed .env.example with Phase 1 keys; not gitignored
expected: Committed .env.example with Phase 1 keys; not gitignored
result: pass
source: automated
coverage_id: 01-01-D4

### 8. GET /me rejects missing/invalid Bearer with 401
expected: GET /me rejects missing/invalid Bearer with 401
result: pass
source: automated
coverage_id: 01-02-D1

### 9. Valid ES256 JWT with allowed corporate email returns CurrentUser from GET /me
expected: Valid ES256 JWT with allowed corporate email returns CurrentUser from GET /me
result: pass
source: automated
coverage_id: 01-02-D2

### 10. Valid JWT with disallowed email domain returns 403 domain_not_allowed
expected: Valid JWT with disallowed email domain returns 403 domain_not_allowed
result: pass
source: automated
coverage_id: 01-02-D3

### 11. Offline ES256 JWKS verify rejects HS256/expired/wrong aud
expected: Offline ES256 JWKS verify rejects HS256/expired/wrong aud
result: pass
source: automated
coverage_id: 01-02-D4

### 12. record_platform_ping stores kind platform_ping via PingRecorder
expected: record_platform_ping stores kind platform_ping via PingRecorder
result: pass
source: automated
coverage_id: 01-03-D1

### 13. POST /me/ping without/invalid Bearer returns 401
expected: POST /me/ping without/invalid Bearer returns 401
result: pass
source: automated
coverage_id: 01-03-D2

### 14. Valid corporate JWT POST /me/ping returns 200 and records platform_ping
expected: Valid corporate JWT POST /me/ping returns 200 and records platform_ping in-memory
result: pass
source: automated
coverage_id: 01-03-D3

### 15. build_in_memory_container exposes pings on AppContainer
expected: build_in_memory_container exposes pings on AppContainer
result: pass
source: automated
coverage_id: 01-03-D4

### 16. SupabasePingRecorder inserts activity_events with kind platform_ping
expected: SupabasePingRecorder inserts activity_events with kind platform_ping via stubbed client
result: pass
source: automated
coverage_id: 01-04-D1

### 17. SupabaseProfileRepository get_or_upsert returns app_role and is idempotent
expected: SupabaseProfileRepository get_or_upsert returns app_role and is idempotent
result: pass
source: automated
coverage_id: 01-04-D2

### 18. build_live_container wires Supabase adapters; create_client only under composition
expected: build_live_container wires Supabase adapters; create_client only under composition
result: pass
source: automated
coverage_id: 01-04-D3

### 19. README documents remote VM connectivity, APP_CONTAINER=live, manual Auth seed
expected: README documents remote VM connectivity, APP_CONTAINER=live, manual Auth seed (PLAT-01/D-08)
result: pass
source: automated
coverage_id: 01-04-D4

### 20. Corporate email domain helper rejects non-ADR-0003 domains
expected: Corporate email domain helper rejects non-ADR-0003 domains
result: pass
source: automated
coverage_id: 01-05-D1

### 21. Disallowed domain shows inline message; signIn not invoked
expected: Disallowed domain shows inline message; signIn not invoked
result: pass
source: automated
coverage_id: 01-05-D2

### 22. Successful login without returnUrl navigates to current issue /
expected: Successful login without returnUrl navigates to current issue /
result: pass
source: automated
coverage_id: 01-05-D3

### 23. returnUrl=/voting returns to /voting after login
expected: returnUrl=/voting returns to /voting after login
result: pass
source: automated
coverage_id: 01-05-D4

### 24. Auth gate redirects unauthenticated users to /login?returnUrl=…
expected: Auth gate redirects unauthenticated users to /login?returnUrl=…
result: pass
source: automated
coverage_id: 01-05-D5

### 25. meApi mock identity + platform ping proof on IssuePage
expected: meApi mock identity + platform ping proof on IssuePage
result: pass
source: automated
coverage_id: 01-05-D6

### 26. Login network failure shows ErrorPanel + Retry (PLAT-07)
expected: Login network failure shows ErrorPanel + Retry (PLAT-07)
result: pass
source: automated
coverage_id: 01-05-D7

### 27. Local platform runbook covers env, uv/uvicorn, Vite, Auth seed, live checklist
expected: Local platform runbook covers env, uv/uvicorn, Vite, Auth seed, live checklist
result: pass
source: automated
coverage_id: 01-06-D1

### 28. Cloud.ru deploy-path doc states Phase 1 does not deploy; linked from README
expected: Cloud.ru deploy-path doc states Phase 1 does not deploy; linked from README
result: pass
source: automated
coverage_id: 01-06-D2

## Summary

total: 28
passed: 27
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

```yaml
- gap_id: G-01-3
  truth: "Corporate login → GET /me → POST /me/ping works; login UX is email+password only; registration is a separate form with a clear name field (ФИО or Имя)"
  status: failed
  reason: "User reported: кнопка Регистрация не активна и не ведёт к регистрации. Форма для входа не должна иметь поля Имя (при каждом входе заполнять нельзя). Форма регистрации должна иметь поле имени с понятной подписью — например ФИО или только Имя."
  severity: major
  test: 3
  root_cause: "Phase 1 never shipped self-service registration (COVERAGE signUp OPT-OUT + D-08 manual Auth seed), but LoginPage shows «Регистрация» as Link to=/login (same route) and puts display-name on the login form after signIn. UI promises a register flow that was never built."
  artifacts:
    - web/src/pages/LoginPage.jsx
    - web/src/App.jsx
    - web/src/services/authApi.js
    - tests/auth.spec.js
    - .planning/phases/01-platform-foundation-auth/COVERAGE.md
    - .planning/debug/g-01-3-registration-ux.md
  missing:
    - "/register route + registration form (or removal of dead Регистрация CTA)"
    - "authApi.signUp if self-service is in scope"
    - "Name field only on registration with clear label"
    - "Login form email+password only"
  debug_session: g-01-3-registration-ux
  decision: |
    Close via self-service registration (amend D-08 / COVERAGE signUp → INTEGRATE).
    Login: email + password only (no name field).
    Registration: email + password + «Логин» (display nickname — любое ненастоящее имя for voting interest; not ФИО).
    «Регистрация» navigates to /register.
```
