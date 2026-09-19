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

## Fix options

1. **Ops (preferred for corp internal):** set `GOTRUE_MAILER_AUTOCONFIRM=true` (or dashboard «Confirm email» off) on knowledge-db.ru so signup does not depend on SMTP.
2. **Ops:** configure working SMTP for GoTrue so confirmation emails send.
3. **App (secondary):** map `error_code` / message containing confirmation email to a clear Russian copy (not generic network); keep Retry for true transport failures.
4. **Product fallback:** if SMTP cannot be fixed soon, document dashboard seed as temporary path and soft-disable Register CTA until mailer works.

## Evidence artifacts

- Browser: RegisterPage ErrorPanel + Retry
- Auth Users: only `test@sberbank.ru`, `test2@omega.sbrf.ru` (no test3)
- curl signup 500 body above
