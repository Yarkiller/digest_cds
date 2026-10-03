---
phase: 13-admin-material-email-preview-honesty
reviewed: 2026-10-03T07:20:00Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - .env.example
  - backend/src/backend/application/ports/mailer.py
  - backend/src/backend/application/use_cases/email_render.py
  - backend/src/backend/application/use_cases/get_admin_shortlist.py
  - backend/src/backend/application/use_cases/preview_digest_email.py
  - backend/src/backend/application/use_cases/send_digest.py
  - backend/src/backend/composition/settings.py
  - backend/src/backend/domain/email_chrome.py
  - backend/src/backend/domain/shortlist.py
  - backend/src/backend/infrastructure/stub_mailer.py
  - backend/src/backend/interface/http/routes/admin.py
  - backend/src/backend/tests_support/in_memory.py
  - docs/agents/local-platform-runbook.md
  - supabase-integration/migrations/010_phase13_scrub_test_header.sql
  - supabase-integration/src/supabase_integration/shortlist_repository.py
  - tests/admin.spec.js
  - tests/unit/test_email_render.py
  - tests/unit/test_http_admin.py
  - tests/unit/test_preview_digest.py
  - tests/unit/test_send_digest.py
  - web/src/pages/AdminDigestPage.jsx
  - web/src/services/adminApi.js
  - web/src/utils/forbiddenChrome.js
findings:
  critical: 1
  warning: 4
  info: 3
  total: 8
status: issues_found
---

# Phase 13: Code Review Report

**Reviewed:** 2026-10-03T07:20:00Z
**Depth:** standard
**Files Reviewed:** 23
**Status:** issues_found

## Summary

Phase 13’s email HTML path is largely sound: `html.escape` in renderers, admin-only preview/send, sandboxed `srcDoc` iframe (no `dangerouslySetInnerHTML`), rehype-sanitize on material markdown, and trusted `Settings.site_url` (not request body). The main defect is a send-path contract bug where `material_ids` and `blocks` can disagree on order, making published issue order diverge from email HTML — undercutting the phase’s preview/send honesty goal for any client that sends both fields.

## Critical Issues

### CR-01: Publish order can diverge from email HTML when both `material_ids` and `blocks` are sent

**File:** `backend/src/backend/application/use_cases/send_digest.py:139-175`
**Issue:** When both `material_ids` and `blocks` are provided, publication order comes from `material_ids` (`ordered_ids` → `claim_and_publish`), while plain/HTML mail order comes from `blocks` via `compose_digest_segments` / `_html_content_blocks`. The docstring claims `material_ids` becomes “publication and mail order”, but mail follows blocks whenever blocks are present. The SPA currently sends matching orders, so the happy path works; any API client (or future FE drift) can publish issue items in one order and email materials in another — breaking digest honesty vs preview.

**Fix:** Derive a single ordered material id list and use it for both publish and mail. Prefer blocks when present (preview parity), else `material_ids`:

```python
effective_ids = (
    _material_ids_from_blocks(blocks)
    if blocks is not None and _material_ids_from_blocks(blocks) is not None
    else material_ids
)
if material_ids is not None and effective_ids is not None and material_ids != effective_ids:
    raise InvalidSendOrderError(batch_id=batch.id)
ordered = _ordered_pool(pool, effective_ids, batch_id=batch.id)
# publish + compose both use `ordered` / same block sequence
```

Alternatively reject requests that supply both with conflicting material order (400 `invalid_send_order`).

## Warnings

### WR-01: Preview accepts material subsets that send rejects

**File:** `backend/src/backend/application/use_cases/preview_digest_email.py:91-112`
**File:** `backend/src/backend/application/use_cases/send_digest.py:80-88,139-141`
**Issue:** `preview_digest_email` / `compose_digest_segments` allow a proper subset of the approved∩ready pool. `send_digest` then requires an exact permutation (`_ordered_pool` / `_material_ids_from_blocks`). The same composition can preview successfully and fail on send with `invalid_send_order` / `empty_send_pool`. The SPA always syncs all approved∩ready into `issueBlocks`, so this is latent for the UI but real for the HTTP API.

**Fix:** Align contracts — either reject subset compositions in preview with `InvalidPreviewCompositionError`, or allow send to publish/mail the composed subset (and document that choice). Prefer matching D-12 “same composition → same HTML”.

### WR-02: Empty/missing slug still emits `Читать →` href to `/materials/`

**File:** `backend/src/backend/application/use_cases/email_render.py:38-44`
**File:** `backend/src/backend/application/use_cases/preview_digest_email.py:126-127,146`
**Issue:** `slug or ""` produces `href="{site}/materials/"` with an empty path segment. Preview and send HTML show a broken reader link instead of omitting the CTA (FE material modal correctly omits the link when slug is blank).

**Fix:**

```python
def render_material_email_block(*, title: str, dek: str | None, slug: str, site_url: str = DEFAULT_SITE_URL) -> str:
    parts = [f"<h2>{html.escape(title, quote=True)}</h2>"]
    if dek and dek.strip():
        parts.append(f"<p>{html.escape(dek.strip(), quote=True)}</p>")
    if slug.strip():
        base = site_url.rstrip("/")
        href = html.escape(f"{base}/materials/{slug.strip()}", quote=True)
        parts.append(f'<p><a href="{href}">Читать →</a></p>')
    return "".join(parts)
```

### WR-03: `SITE_URL` / `site_url` not restricted to `http:` / `https:`

**File:** `backend/src/backend/composition/settings.py:47-51`
**File:** `backend/src/backend/application/use_cases/email_render.py:38-39`
**Issue:** `site_url` is concatenated into email `href`s with only `html.escape`. A mis-set env value such as `javascript:...` or `data:...` becomes a dangerous link in outbound HTML (future SMTP) and in admin preview markup (mitigated today by `sandbox=""`). Operator-controlled, but cheap to validate at Settings load.

**Fix:**

```python
from urllib.parse import urlparse

def _validated_site_url(raw: str, default: str) -> str:
    parsed = urlparse(raw)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return raw.rstrip("/")
    return default
```

Apply in `Settings.from_env` before storing `site_url`.

### WR-04: Material modal invents `~1 мин` when `reading_minutes` is null/non-finite

**File:** `web/src/pages/AdminDigestPage.jsx:903-905`
**Issue:** `Number.isFinite(item.reading_minutes) ? item.reading_minutes : 1` displays one minute whenever the API omits or nulls `reading_minutes`. Char/word counts honestly fall back to `0`; reading time does not. Live shortlist rows with null `reading_minutes` look like a 1-minute read. (Empty-body Playwright mock sets `reading_minutes: 1` explicitly — that fixture is fine; the silent FE default is not.)

**Fix:**

```javascript
const readingMinutes = Number.isFinite(item.reading_minutes) ? item.reading_minutes : 0
```

Update the empty-body E2E expectation only if the mock stops setting `reading_minutes: 1`.

## Info

### IN-01: Mock preview slug fallback diverges from backend

**File:** `web/src/services/adminApi.js:463-466`
**Issue:** Mock HTML uses `item.slug || String(item.material_id)`; backend uses `slug or ""` and can emit `/materials/`. Playwright-on-mocks can hide missing-slug honesty gaps.
**Fix:** Use the same empty-slug rule as `render_material_email_block` (omit CTA or emit `/materials/` consistently).

### IN-02: Mock `escapeHtml` does not escape `'` (Python `html.escape(..., quote=True)` does)

**File:** `web/src/services/adminApi.js:415-421`
**Issue:** Minor mock/live parity gap for apostrophes inside attributes; current hrefs use double quotes so risk is low.
**Fix:** Add `.replace(/'/g, '&#x27;')` to match CPython `html.escape(..., quote=True)`.

### IN-03: Send imports private `_html_content_blocks` from preview module

**File:** `backend/src/backend/application/use_cases/send_digest.py:15-20`
**Issue:** Cross-use-case dependency on a private helper increases breakage risk when preview internals change.
**Fix:** Move `_html_content_blocks` (and shared composition helpers) into `email_render.py` or a small shared composition module imported by both use cases.

---

_Reviewed: 2026-10-03T07:20:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
