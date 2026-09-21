---
phase: 05-admin-digest-publish
reviewed: 2026-09-21T15:50:00Z
depth: standard
files_reviewed: 38
files_reviewed_list:
  - backend/src/backend/domain/shortlist.py
  - backend/src/backend/domain/current_user.py
  - backend/src/backend/domain/errors.py
  - backend/src/backend/application/ports/shortlist_repository.py
  - backend/src/backend/application/ports/issue_repository.py
  - backend/src/backend/application/ports/mailer.py
  - backend/src/backend/application/use_cases/get_admin_shortlist.py
  - backend/src/backend/application/use_cases/set_shortlist_decision.py
  - backend/src/backend/application/use_cases/preview_digest_email.py
  - backend/src/backend/application/use_cases/send_digest.py
  - backend/src/backend/application/use_cases/get_current_user.py
  - backend/src/backend/infrastructure/stub_mailer.py
  - backend/src/backend/interface/http/deps.py
  - backend/src/backend/interface/http/routes/admin.py
  - backend/src/backend/interface/http/routes/me.py
  - backend/src/backend/interface/http/app.py
  - backend/src/backend/composition/container.py
  - backend/src/backend/composition/live.py
  - backend/src/backend/composition/settings.py
  - backend/src/backend/tests_support/in_memory.py
  - supabase-integration/migrations/005_phase5_admin_shortlist.sql
  - supabase-integration/src/supabase_integration/shortlist_repository.py
  - supabase-integration/src/supabase_integration/issue_repository.py
  - supabase-integration/src/supabase_integration/__init__.py
  - web/src/services/adminApi.js
  - web/src/services/meApi.js
  - web/src/services/authEnv.js
  - web/src/pages/AdminDigestPage.jsx
  - web/src/pages/ForbiddenPage.jsx
  - web/src/pages/LoginPage.jsx
  - web/src/components/AppShell.jsx
  - web/src/App.jsx
  - web/src/main.jsx
  - playwright.config.js
  - tests/admin.spec.js
  - tests/auth.spec.js
  - tests/unit/test_http_admin.py
  - tests/unit/test_send_digest.py
findings:
  critical: 1
  warning: 5
  info: 2
  total: 8
resolved:
  - CR-01
  - WR-02
open:
  - WR-01
  - WR-03
  - WR-04
  - WR-05
  - IN-01
  - IN-02
status: issues_found
fix_applied: 2026-09-21T16:05:00Z
---

# Phase 05: Code Review Report

**Reviewed:** 2026-09-21T15:50:00Z
**Depth:** standard
**Files Reviewed:** 38
**Status:** issues_found

## Summary

Phase 05 admin digest publish was reviewed with focus on `require_admin` / `profiles.role`, shortlist decision + publish-on-send, StubMailer / ADMIN-08 `returnUrl`, and SPA AdminDigest / Forbidden pages.

Authorization is correctly profile-based (`require_admin` → `get_current_user` → `profiles.role`; JWT `role` is only the Supabase `"authenticated"` claim). ADMIN-08 `sanitizeReturnUrl` correctly rejects protocol-relative `//` open redirects. StubMailer + `MAILER=smtp` fail-fast wiring look sound.

The main defect is non-atomic live send: `claim_sent` then `IssueRepository.publish` without using migration `claim_and_publish_digest`, so a publish failure permanently claims the batch with no recoverable retry. Secondary gaps: delivery columns never written on the Python path, demo `score_factors` honesty broken by empty `factors: []`, in-memory `get_current_batch` ignoring `sent_at`, and SPA `issue_url` rendered without path sanitization.

## Critical Issues

### CR-01: Claim-then-publish is not atomic — stuck `sent_at` without issue  — ✅ RESOLVED (2026-09-21)

**Resolution:** Added a `ShortlistRepository.release_claim(batch_id)` compensating action (in-memory + Supabase adapters) and wrapped `IssueRepository.publish` in `send_digest` with a `try/except` that releases the claim and re-raises on any publish failure. A failed publish now returns the batch to the unsent pool so a retry can succeed instead of wedging it as claimed-but-unpublished. Covered by `test_send_publish_failure_releases_claim_for_retry` (use case) and `test_release_claim_clears_sent_at_for_retry` / `test_release_claim_maps_sdk_failure_to_persistence_error` (adapter contract). The fully-atomic single-transaction path (migration 005 `claim_and_publish_digest` RPC) remains the recommended follow-up — tracked under WR-01.



**File:** `backend/src/backend/application/use_cases/send_digest.py:79-102`
**Also:** `supabase-integration/src/supabase_integration/shortlist_repository.py:122-151`, `supabase-integration/src/supabase_integration/issue_repository.py:174-234`, `supabase-integration/migrations/005_phase5_admin_shortlist.sql:21-96`

**Issue:** `send_digest` claims the batch (`sent_at` set, `WHERE sent_at IS NULL`) **before** `issues.publish`. If publish fails (unique `digest_issues.number` race, material resolve failure, item insert error, network/SDK error), the batch stays claimed. Retry hits `AlreadySentError` / HTTP 409; no issue, no delivery columns, no automated recovery. Migration 005 already defines `claim_and_publish_digest` for a single-transaction claim+publish, but `SupabaseShortlistRepository.claim_sent` deliberately does ordered UPDATE only and never calls the RPC.

**Fix:** Prefer the RPC (or equivalent single DB transaction) so claim and publish commit/rollback together:

```python
# Prefer in SupabaseShortlistRepository (or a dedicated publish_digest port):
# rpc("claim_and_publish_digest", {...}) → batch + issue_number + issue_url
# On RPC failure: no sent_at stamp; client can retry safely.
#
# If keeping split use-case: on publish PersistenceError after claim,
# compensate (clear sent_at) or fail closed without claiming until publish succeeds.
```

Minimum viable compensation if RPC cannot be wired yet:

```python
try:
    claimed = shortlist.claim_sent(...)
    published = issues.publish(...)
except PersistenceError:
    # must un-claim or never have claimed — otherwise batch is dead
    raise
```

## Warnings

### WR-01: Delivery columns from migration 005 never written on live Python path

**File:** `supabase-integration/src/supabase_integration/shortlist_repository.py:134-151`
**Also:** `backend/src/backend/application/use_cases/send_digest.py:111-140`, `supabase-integration/migrations/005_phase5_admin_shortlist.sql:7-19`

**Issue:** `005` adds `delivery_status`, `recipient_count`, `published_issue_id`, `issue_url` and the RPC stamps them. Live `claim_sent` only sets `sent_at`. After a successful send, audit fields stay NULL — ADMIN-07 / D-87 delivery honesty is incomplete for operators and any future UI that reads those columns.

**Fix:** After successful publish+mail (or inside RPC), update the batch:

```python
# After publish + mailer.send_digest:
self._client.table("digest_shortlist_batches").update({
    "delivery_status": delivery_status,
    "recipient_count": recipient_count,
    "published_issue_id": published.id,
    "issue_url": issue_url,
}).eq("id", claimed.id).execute()
```

Or route send through `claim_and_publish_digest` which already stamps these fields.

### WR-02: `honest_factor_labels` treats empty `factors: []` as authoritative — demo seed shows «обоснование недоступно»  — ✅ RESOLVED (2026-09-21)

**Resolution:** `honest_factor_labels` now takes the structured-list branch only when `factors` is a **non-empty** list (`isinstance(factors, list) and factors`); an empty `factors: []` falls through to the flat-key branch. The `rag-systems` demo row now surfaces its two flat labels. Covered by `test_honest_factor_labels_falls_back_to_flat_keys_when_factors_list_empty`. The demo seed JSON was left unchanged (behavioral fix is source of truth).



**File:** `backend/src/backend/domain/shortlist.py:18-34`
**Also:** `supabase-integration/migrations/005_phase5_admin_shortlist.sql:160-166`

**Issue:** When `score_factors` contains `"factors": []` **and** flat human keys (as in the Phase 5 demo seed for `rag-systems`), the helper takes the list branch, gets zero labels, and returns `[]` without falling back to flat keys. ADMIN-05 honesty then shows «обоснование недоступно» for a row that has ≥2 readable flat labels.

**Fix:**

```python
factors = score_factors.get("factors")
if isinstance(factors, list) and factors:
    labels = [...]
else:
    labels = [
        str(k).strip()
        for k, _v in score_factors.items()
        if str(k).strip() and k != "factors"
    ]
```

Or remove `"factors": []` from the demo seed JSON.

### WR-03: In-memory `get_current_batch` ignores `sent_at` (contract drift vs live)

**File:** `backend/src/backend/tests_support/in_memory.py:77-78`

**Issue:** Port contract says “latest unsent batch (`sent_at IS NULL`)”. Live filters `.is_("sent_at", "null")`. In-memory returns `_batch` even after `claim_sent`, so post-send GET still returns the sent batch and `set_shortlist_decision` can mutate a claimed batch — masking bugs that would 404/empty on live.

**Fix:**

```python
def get_current_batch(self) -> ShortlistBatch | None:
    if self._batch is None or self._batch.sent_at is not None:
        return None
    return self._batch
```

### WR-04: SPA renders `issue_url` via `<Link to={issueUrl}>` without same-origin sanitization

**File:** `web/src/pages/AdminDigestPage.jsx:246-246`, `web/src/pages/AdminDigestPage.jsx:466-472`
**Also:** `web/src/services/authEnv.js:19-28`

**Issue:** Backend currently hardcodes `issue_url = f"/issues/{n}"` (safe). The SPA trusts `result.issue_url` as a React Router `to` value. A compromised/proxied response with `//evil.example/...` or absolute URL would bypass ADMIN-08’s `sanitizeReturnUrl` (used only on login/register). Defense-in-depth gap for the D-90 CTA.

**Fix:**

```javascript
import { sanitizeReturnUrl } from '../services/authEnv.js'
// ...
setIssueUrl(sanitizeReturnUrl(result.issue_url))
// Link only when issueUrl !== '/' or when path matches /^\/issues\/\d+$/
```

### WR-05: Batch Approve/Reject stops mid-loop — partial persist, generic toast

**File:** `web/src/pages/AdminDigestPage.jsx:201-217`

**Issue:** `applyDecision` awaits `setDecision` sequentially. If item N fails after 1…N−1 succeeded, earlier mutations are already persisted; UI applies the last successful snapshot and shows «Не сохранено» without identifying which IDs failed. Risk of inconsistent triage state vs operator expectation of all-or-nothing.

**Fix:** Collect failures; on any error either continue and report failed IDs, or use a bulk decision endpoint / compensating rollback messaging:

```javascript
const failed = []
for (const id of ids) {
  try {
    latest = await setDecision(id, decision)
  } catch {
    failed.push(id)
  }
}
if (failed.length) setToast(`Не сохранено: ${failed.length}`)
```

## Info

### IN-01: Context / schema textareas are local-only dead UI

**File:** `web/src/pages/AdminDigestPage.jsx:74-75`, `web/src/pages/AdminDigestPage.jsx:357-381`

**Issue:** `contextText` / `schemaText` never reach preview or send APIs. Operators can edit them expecting digest content change; stub email ignores them. Confusing UX, not a security bug.

**Fix:** Wire into preview/send payloads when product requires it, or remove/hide until PIPE / editor scope lands.

### IN-02: HTTP `AdminShortlistResponse` omits `sent_at` / `week_label` that SPA expects

**File:** `backend/src/backend/interface/http/routes/admin.py:39-43`
**Also:** `backend/src/backend/domain/shortlist.py:69-72`, `web/src/pages/AdminDigestPage.jsx:40-46`

**Issue:** SPA `applyBatch` reads `dto.sent_at` / `dto.week_label`, but live GET never returns them (`AdminShortlist` has only `batch_id` + `items`). Live week dek never shows; `sent_at` gate relies on client state / empty next batch after claim. Harmless with current empty-after-send behavior; contract mismatch with mocks.

**Fix:** Extend DTO/response with `sent_at` / `week_label` from `ShortlistBatch`, or stop reading them in the SPA for live mode.

---

## Fix-session triage (2026-09-21) — remaining warnings

Reviewed each open warning for validity, severity, and fix risk. Verdicts:

| ID | Verdict | Recommended action | Risk / why deferred |
|----|---------|--------------------|---------------------|
| **WR-01** | **Valid** — delivery columns (`delivery_status`, `recipient_count`, `published_issue_id`, `issue_url`) stay NULL on the live Python path after a successful send. | Route send through the `claim_and_publish_digest` RPC (also closes CR-01 atomicity fully), **or** add a post-publish `update(...)` on the batch. Prefer the RPC. | Needs a new port method (e.g. `publish_digest`) or an extra adapter write + a Supabase-contract test that asserts the columns are stamped. Larger than a use-case-local change; not blindly auto-applied. Recommend doing next. |
| **WR-03** | **Valid** — in-memory `get_current_batch` ignores `sent_at`, drifting from the live `sent_at IS NULL` contract. | Return `None` when `_batch.sent_at is not None`. | ⚠️ Conflicts with 3 existing `send_digest` tests that assert `get_current_batch().sent_at == now` post-send. Fixing correctly also means giving those tests a sent-batch accessor. Small but touches test expectations — recommend a dedicated pass so the intent stays clear. |
| **WR-04** | **Valid (defense-in-depth)** — SPA renders `result.issue_url` as a Router `to` without same-origin sanitization; backend value is currently safe (`/issues/{n}`). | Pass `issue_url` through `sanitizeReturnUrl` / gate on `/^\/issues\/\d+$/` before `<Link>`. | Frontend change → requires a Playwright/unit test per repo TDD. Deferred to a UI-scoped fix session. |
| **WR-05** | **Valid** — batch Approve/Reject stops mid-loop; partial persist with a generic toast. | Collect failed IDs, continue, and report which IDs failed (or add a bulk endpoint). | Frontend + UX decision (all-or-nothing vs best-effort). Needs Playwright coverage. Deferred to UI session. |
| IN-01 / IN-02 | Info only | As noted in each finding. | Non-blocking. |

**Applied this session:** CR-01 (compensation), WR-02 (honesty fallback) — both TDD, full suite green (229 passed).
**Recommended next:** WR-01 (RPC) → then WR-03; WR-04/WR-05 in a UI-scoped session.

---

## Focus-area notes (no separate findings)

| Area | Verdict |
|------|---------|
| `require_admin` / profiles.role | **OK** — `deps.require_admin` uses `get_current_user` → profiles; JWT `role` must be `"authenticated"` only (`auth_jwt.py`), never app admin |
| StubMailer / `resolve_mailer` | **OK** — stub logs + `delivery_status=stubbed`; `MAILER=smtp` raises at composition |
| ADMIN-08 `sanitizeReturnUrl` | **OK** — rejects non-`/`, `//`, `://`; login/register navigate sanitized; Playwright covers `/issues/13` and `//evil` |
| ForbiddenPage / AdminDigest gate | **OK** — deep-link non-admin → Forbidden; API still `require_admin` (defense in depth). NavLink role from `fetchMe.role` |

---

_Reviewed: 2026-09-21T15:50:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
