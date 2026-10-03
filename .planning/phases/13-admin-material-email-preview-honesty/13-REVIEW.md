---
phase: 13-admin-material-email-preview-honesty
reviewed: 2026-10-03T09:27:25Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - tests/admin.spec.js
  - web/src/components/PlatformProofBanner.jsx
  - web/src/pages/AdminDigestPage.jsx
  - web/src/pages/LoginPage.jsx
  - web/src/pages/RegisterPage.jsx
  - web/src/services/adminApi.js
  - web/src/services/meApi.js
  - web/src/services/welcomeSession.js
findings:
  critical: 0
  warning: 3
  info: 3
  total: 6
status: issues_found
---

# Phase 13: Code Review Report

**Reviewed:** 2026-10-03T09:27:25Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Incremental review since `fbccc6e` (plans 13-07, 13-08, and `0c6dd13`). Pinned preview headers, the removed email item list, and the sticky `window.__DIGEST_ME_FAIL_FETCH__` outage match their stated contracts. The welcome toast can still be torn down on the issue page’s loading-to-ready remount, and a `sessionStorage` failure after a successful sign-in aborts navigation. The material dialog still invents a one-minute read when `reading_minutes` is missing.

## Warnings

### WR-01: Welcome toast unmounts when the issue leaves loading

**File:** `web/src/components/PlatformProofBanner.jsx:16-51`
**Issue:** The toast state and the 5s dismiss timer live only in this effect. `IssuePage` mounts a separate `<PlatformProofBanner />` in the loading branch (`web/src/pages/IssuePage.jsx:30`) and another in the ready branch (`web/src/pages/IssuePage.jsx:161`). Leaving loading unmounts the first instance: cleanup sets `cancelled` and clears `dismissTimer` before `clearWelcomeToast()` runs. The session flag survives, so the next instance can show the toast again, but any toast already on screen disappears and the dismiss deadline starts over after a second `fetchMe`. On a slow issue load that loses the race to `/me`, the user sees the toast vanish and return. The auth test only asserts visibility after the page has settled, so it does not catch the gap.

**Fix:** Render one banner above the status switch so loading and ready share the same instance:

```jsx
export default function IssuePage({ isCurrent = true }) {
  // ...existing state and effects...
  const statusView = status !== 'ready' || notFound || isEmpty
  return (
    <>
      {isCurrent ? <PlatformProofBanner /> : null}
      {statusView ? (
        <IssueStatusView status={status} notFound={notFound} isEmpty={isEmpty} isCurrent={false} reload={reload} />
      ) : (
        <section data-testid="issue-ready">{/* ready body without a second banner */}</section>
      )}
    </>
  )
}
```

Remove the other `<PlatformProofBanner />` copies inside `IssueStatusView`.

### WR-02: Storage failure after sign-in is reported as a failed login

**File:** `web/src/services/welcomeSession.js:4-7`
**Issue:** `armWelcomeToast()` calls `sessionStorage.setItem` with no try/catch. `LoginPage` (`web/src/pages/LoginPage.jsx:48-52`) and `RegisterPage` (`web/src/pages/RegisterPage.jsx:64-68`) call it only after auth (and, on register, after display-name writes) succeed. If storage is blocked, `setItem` throws `SecurityError`. That exception is not an `AuthApiError` / `MeApiError`, so the page catch shows «Сервис входа временно недоступен» and never calls `navigate`. The session is already established.

**Fix:** Swallow storage failures inside the helper so the auth success path always continues:

```javascript
function storage() {
  try {
    if (typeof sessionStorage === 'undefined') return null
    return sessionStorage
  } catch {
    return null
  }
}

export function armWelcomeToast() {
  try {
    storage()?.setItem(WELCOME_KEY, '1')
  } catch {
    // Login and register must still navigate.
  }
}
```

Apply the same try/catch in `peekWelcomeToast` and `clearWelcomeToast`.

### WR-03: Material preview shows one minute when reading time is missing

**File:** `web/src/pages/AdminDigestPage.jsx:900`
**Issue:** `Number.isFinite(item.reading_minutes) ? item.reading_minutes : 1` renders «~1 мин» when the shortlist omits `reading_minutes` or sends `null`. Character and word counts on the next lines fall back to `0`. A row with an unknown duration looks like a one-minute read. The empty-body mock sets `reading_minutes: 1` itself; this default is the live-DTO path. Plan 13-07 moved this line into the new scroll body and left the fallback in place.

**Fix:**

```javascript
const readingMinutes = Number.isFinite(item.reading_minutes) ? item.reading_minutes : 0
```

## Info

### IN-01: `postPing` has no remaining caller

**File:** `web/src/services/meApi.js:183-231`
**Issue:** `0c6dd13` removed the banner’s ping button, and nothing else in `web/` or `tests/` calls `postPing`. The helper still honors the one-shot `failNextFetch` flag and not the sticky `__DIGEST_ME_FAIL_FETCH__` outage, so a future caller would disagree with `fetchMe`.
**Fix:** Delete `postPing` until a caller needs it, or route it through the same sticky check as `fetchMe`.

### IN-02: Mock email HTML invents a slug the backend omits

**File:** `web/src/services/adminApi.js:471-474`
**Issue:** `item.slug || String(item.material_id)` always emits a `Читать →` href. Backend `render_material_email_block` uses `slug or ""` and can emit `/materials/` with an empty segment. Playwright-on-mocks will not show that broken link.
**Fix:** Use the same empty-slug rule as the backend renderer (omit the anchor when slug is blank).

### IN-03: Mock `escapeHtml` does not escape apostrophes

**File:** `web/src/services/adminApi.js:423-429`
**Issue:** The helper escapes `&`, `<`, `>`, and `"`. Python `html.escape(..., quote=True)` also escapes `'`. Current mock hrefs use double quotes, so this does not break today’s attributes, but text that later lands in a single-quoted attribute will diverge from live mail.
**Fix:** Add `.replace(/'/g, '&#x27;')` to match CPython `html.escape(..., quote=True)`.

---

_Reviewed: 2026-10-03T09:27:25Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
