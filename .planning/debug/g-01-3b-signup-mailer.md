# Debug: G-01-3b registration signup 500

**Date:** 2026-09-19  
**Symptom:** SPA shows retryable «Сервис входа временно недоступен»; user `test3@sberbank.ru` never appears in Auth Users.

## Probe (reproduce)

`POST https://knowledge-db.ru/auth/v1/signup` with publishable apikey:

```json
{"code":500,"error_code":"unexpected_failure","msg":"Error sending confirmation email"}
```

`GET /auth/v1/settings`:

- `disable_signup`: false (signups allowed)
- `mailer_autoconfirm`: **false** (confirmation email required)
- `external.email`: true

`GET /auth/v1/health`: 200 GoTrue v2.196.0

## Root cause

Self-service `signUp` reaches GoTrue, but Auth fails while **sending the confirmation email** (SMTP / mailer misconfigured or unreachable on the shared VM). GoTrue returns HTTP 500 → supabase-js surfaces as retryable / AuthRetryableFetchError → SPA maps to NETWORK ErrorPanel. User row is not persisted (or is rolled back) because confirmation mail send failed.

This is **not** an SPA routing/UI bug from 01-07; the FE correctly calls `supabase.auth.signUp`. Login with existing dashboard-seeded users can still work (no confirmation mail on password grant).

## Fix options (operator decision 2026-09-19)

**Chosen path = option 3, split:**

1. **Autoconfirm now** — unblock UAT Test 3 (`Confirm email` OFF / `GOTRUE_MAILER_AUTOCONFIRM=true`). See runbook §4.1.
2. **SPA error UX** — **deferred follow-up** (not blocking Phase 1 seal): map confirmation-mailer failures to honest Russian copy; never lie with generic NETWORK «Сервис входа временно недоступен».
3. **SMTP** — **ops ticket, not Phase 1.** Document and do not ship email-dependent features until mailer is healthy. Revisit later.

## Evidence artifacts

- Browser: RegisterPage ErrorPanel + Retry
- Auth Users: only `test@sberbank.ru`, `test2@omega.sbrf.ru` (no test3)
- curl signup 500 body above
