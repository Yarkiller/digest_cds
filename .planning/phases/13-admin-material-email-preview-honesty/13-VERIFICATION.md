---
phase: 13-admin-material-email-preview-honesty
verified: 2026-10-03T09:34:00Z
status: passed
score: 15/15 must-haves verified
covered_files:
  - .env.example
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-FIX-01-LOCK.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-01-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-01-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-02-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-02-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-03-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-03-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-04-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-04-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-05-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-05-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-06-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-06-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-07-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-07-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-08-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-08-SUMMARY.md
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
covered_digest: "v2:sha256:6e0d39f8929b902a5ca86410944958735bda3d8b5d682fa5cb8d140a7757d35c"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 10/14
  gaps_closed:
    - "Material preview close stays in view with cursor-pointer while the body scrolls (UAT G-13-1, G-13-2)"
    - "Email preview close stays in view with cursor-pointer while the preview scrolls (UAT G-13-3)"
    - "Email preview success view is subject plus sandboxed iframe; numbered preview.items list is not rendered (UAT G-13-3b)"
  gaps_remaining: []
  regressions: []
deferred:
  - truth: "Reader page at /materials/<slug> loads without an error when opened from the admin preview link"
    addressed_in: "Phase 999.1 and Phase 999.2"
    evidence: "ROADMAP backlog: reader /materials/<slug> error page is filed as not Phase 13 scope (UAT O3). Phase 13 proves the href /materials/<slug>."
---

# Phase 13: Admin material & email preview honesty Verification Report

**Phase Goal:** Admin can inspect a real material body and a real email HTML preview before send
**Verified:** 2026-10-03T09:34:00Z
**Status:** passed
**Re-verification:** Yes — after UAT gap closure (plans 13-07 and 13-08). The prior report was `human_needed` (10/14) and had no `gaps:` frontmatter; the failures lived in `13-UAT.md`. That report was not treated as proof.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ------- | ------ | -------------- |
| 1 | On `/admin/digest`, material preview shows `body_markdown`, `provenance_label`, char/word counts, and a link to `/materials/<slug>` (not title+dek only) | ✓ VERIFIED | `AdminItemPreview` renders title → provenance → `~{char} символов · {word} слов · ~{min} мин` → Markdown body → `Открыть материал →` (`AdminDigestPage.jsx`). Named unit `test_admin_shortlist_returns_full_items` **PASS** this pass. Playwright case `material preview shows body_markdown provenance counts and reader link` asserts the href |
| 2 | «Превью письма» renders real email HTML including intro, summaries, and links (not titles-only) | ✓ VERIFIED | `render_email_html` emits intro `<p>`, material `<h2>`, and `Читать →`. Live `previewEmail` returns `response.json()`. Iframe `sandbox=""` `srcDoc={preview.html}`. Unit `test_render_email_html_applies_interstitial_to_intro_and_includes_material` **PASS**. Playwright `preview lists one approved-ready article` **PASS** (title read from the iframe heading) |
| 3 | Interstitial connecting text preserves paragraph breaks so `\n\n` is visible as separate paragraphs | ✓ VERIFIED | `render_interstitial_html` splits on `\n\n` into `<p>` and single `\n` into `<br>`. Unit `test_render_interstitial_html_two_paragraphs_via_blank_line` **PASS** (`one\n\ntwo` → `<p>one</p><p>two</p>`). `test_preview_html_present_with_interstitial_paragraphs` **PASS** |
| 4 | Leaked `test-header` (and equivalent seed/test chrome) does not appear on admin preview surfaces after cleanup | ✓ VERIFIED | Migration `010_phase13_scrub_test_header.sql` still checked in. Runbook §4g **Applied 2026-10-03** with empty `title ilike %test-header%` probe. `test_python_forbidden_lower_matches_js_mirror` **PASS**. `email_render.py` does not import the ban helper. Playwright ban-surface cases remain in `tests/admin.spec.js` |
| 5 | GET `/admin/shortlist` enrichment uses the materials join only — keys `body_markdown`, `provenance_label`, `slug`, `reading_minutes`, `char_count`, `word_count`; `extra=forbid` retained | ✓ VERIFIED | `shortlist_repository.py` select includes those columns. `AdminShortlistItemResponse` and `AdminShortlistResponse` keep `ConfigDict(extra="forbid")`. No `/admin/materials` route on the admin router |
| 6 | Material modal uses the enriched shortlist DTO only (no fetch-on-open); markdown stack + honest empty body | ✓ VERIFIED | `AdminItemPreview({ item })` — no fetch. `Markdown` + `remarkGfm` + `rehypeSanitize` + `rehypeSlug`. Empty body copy «Текст материала недоступен». Playwright request spy expects zero `/admin/materials/` hits |
| 7 | Email preview surface is sandboxed backend `html` via iframe; the live SPA does not invent HTML; loading/error copy is honest | ✓ VERIFIED | iframe `sandbox=""` + `srcDoc`. `composeMockPreviewHtml` runs only inside `previewEmail`'s `useMocks()` branch. Loading «Загрузка…» / error «Превью недоступно» + «Повторить превью» sit under the pinned header |
| 8 | `send_digest` uses the same `render_email_html` + trusted `Settings.site_url` as preview | ✓ VERIFIED | Both admin POSTs pass `settings.site_url`. Named unit `test_preview_email_html_matches_send_html` **PASS**. Issue URL is prepended on the plain send body only (`send_digest.py`), not inside `render_email_html` |
| 9 | Ban helpers are assert-only; Python and JS lists match; scrub migration + shared-VM apply evidence remain (ADUX-04) | ✓ VERIFIED | `test_python_forbidden_lower_matches_js_mirror` **PASS**. `test_email_render_module_does_not_import_or_call_ban_helper` **PASS**. §4g Applied line unchanged by gap closure |
| 10 | Connecting-text and intro show muted hint «Пустая строка = новый абзац» | ✓ VERIFIED | Two hint spans remain in `AdminDigestPage.jsx` (intro textarea and issue text block). UAT test 4 result: pass. Playwright hint case still present. Gap-closure plans did not retarget that markup |
| 11 | On the material preview dialog, «Закрыть» stays in view while the markdown body scrolls, uses `cursor-pointer`, and the header row is outside `overflow-y-auto` (G-13-1, G-13-2) | ✓ VERIFIED | Shell is `flex` / `max-h-[90vh]` / `overflow-hidden`; header `shrink-0`; scroll region `min-h-0 flex-1 overflow-y-auto`; close `cursor-pointer`. Playwright `material preview close stays visible while the body scrolls` **PASS** this pass (`insideOverflow` false, `scrollHeight > clientHeight`, close in viewport) |
| 12 | On the email preview dialog, the same close control stays in view while subject and iframe scroll, and uses `cursor-pointer` (G-13-3) | ✓ VERIFIED | Same shell on the email dialog. Playwright `email preview close stays visible while the preview scrolls` **PASS** this pass at 1280×400 (`ul` count 0, close in viewport, scroll region overflows) |
| 13 | Successful email preview shows the subject and the sandboxed iframe only; no numbered `preview.items` list and no `preview.body` node (G-13-3b) | ✓ VERIFIED | Success branch renders subject + `email-preview-frame` only. No `preview.items`, `preview.body`, or `email-preview-body` in `AdminDigestPage.jsx`. No `emailDialog.locator("li")` left in `tests/admin.spec.js`. Playwright one-article case **PASS** with dialog `ul` count 0 |
| 14 | Long titles and provenance wrap with `break-words` in the material modal | ✓ VERIFIED | `break-words` remains on title and provenance inside the scroll region after the shell split. UAT test 1 reported the wrap expectation as pass; the observations were close position and cursor, now covered by truth 11 |
| 15 | Long connecting text wraps in the textarea; the hint stays visible below | ✓ VERIFIED | Intro textarea keeps the hint as the next sibling (`mt-1 block`). UAT test 4 result: pass. That block was not part of plans 13-07 or 13-08 |

**Score:** 15/15 truths verified (0 present, behavior-unverified)

UAT G-13-3c (single connecting line looks flat in the iframe) is not a markup defect. `render_interstitial_html("hello")` is one `<p>hello</p>`. A line with no blank line is one paragraph. `\n\n` is what splits paragraphs (truth 3, unit-tested this pass).

### Deferred Items

| # | Item | Addressed In | Evidence |
| --- | ------ | ------------- | ---------- |
| 1 | Reader `/materials/<slug>` returns an error page when the admin link is opened | Phase 999.1 and Phase 999.2 | ROADMAP backlog follow-ups from UAT O3. Phase 13's contract is the href on the preview link, which the Playwright material case asserts |

### Advisory (New Scope, Unevidenced)

None. Re-verification scanned `AdminDigestPage.jsx`, `adminApi.js`, and `tests/admin.spec.js` (the files gap closure changed). No new-scope blocker without a failing test.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `tests/unit/test_http_admin.py` | Full-item DTO proof | ✓ VERIFIED | `test_admin_shortlist_returns_full_items` green this pass |
| `backend/.../domain/shortlist.py` | ShortlistItem + counts | ✓ VERIFIED | `material_counts` present |
| `supabase-integration/.../shortlist_repository.py` | Widened materials select | ✓ VERIFIED | Join includes body, slug, provenance, reading_minutes |
| `backend/.../email_render.py` | Shared HTML renderers | ✓ VERIFIED | interstitial + material block + compose |
| `tests/unit/test_email_render.py` | Interstitial and ban coverage | ✓ VERIFIED | Paragraph and ban-sync tests green this pass |
| `backend/.../preview_digest_email.py` | Preview html | ✓ VERIFIED | Calls `render_email_html` |
| `backend/.../domain/email_chrome.py` | FORBIDDEN_LOWER assert-only | ✓ VERIFIED | Not imported by `email_render.py` |
| `web/src/pages/AdminDigestPage.jsx` | Pinned dialogs + iframe, no items list | ✓ VERIFIED | Header outside scrollport; success branch is subject + iframe |
| `web/src/services/adminApi.js` | Live JSON preview; mock-only long body | ✓ VERIFIED | `__DIGEST_ADMIN_MATERIAL_LONG_BODY__` only inside `useMocks()` |
| `tests/admin.spec.js` | Close-scroll and list-removal proofs | ✓ VERIFIED | Three named Playwright tests green this pass |
| `backend/.../send_digest.py` | Shared render on send | ✓ VERIFIED | `render_email_html` + plain issue URL wrapper |
| `backend/.../routes/admin.py` | Preview/send `site_url` wire | ✓ VERIFIED | Both POSTs pass trusted Settings |
| `tests/unit/test_preview_digest.py` | Preview≡send HTML | ✓ VERIFIED | `test_preview_email_html_matches_send_html` green this pass |
| `010_phase13_scrub_test_header.sql` | Idempotent scrub | ✓ VERIFIED | File present; apply recorded in runbook §4g |
| `docs/agents/local-platform-runbook.md` | Apply/verify scrub | ✓ VERIFIED | §4g Applied 2026-10-03 |
| `web/src/utils/forbiddenChrome.js` | JS ban mirror | ✓ VERIFIED | Sync unit green this pass |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | ------ | ------- | ------- |
| `materials(...)` join | `AdminShortlistItemResponse` JSON | `ShortlistRepository.get_current_batch` → use-case → `_to_response` | ✓ WIRED | Select columns match DTO fields; full-item unit green |
| `render_email_html` + `Settings.site_url` | `DigestPreviewResponse.html` | `preview_digest_email` | ✓ WIRED | Preview route sets `html=preview.html` |
| `AdminShortlistItem.body_markdown` | `AdminItemPreview` Markdown | Shortlist DTO already on the page | ✓ WIRED | No second network call on modal open |
| `POST /admin/shortlist/preview` `html` | iframe `srcDoc` | `adminApi.previewEmail` → email dialog | ✓ WIRED | `data-testid=email-preview-frame`; live path returns `response.json()` |
| Dialog header row | Close button | Header is a sibling of `overflow-y-auto`, not a descendant | ✓ WIRED | Playwright `insideOverflow === false` on both dialogs |
| `previewEmail` html | iframe only | Success branch minus the items `ul` | ✓ WIRED | No `preview.items` map; Playwright `ul` count 0 |
| `010` scrub SQL | Clean admin preview surfaces | Operator §4g apply + regression asserts | ✓ WIRED | Applied evidence unchanged; ban unit green |
| `settings.site_url` (send POST) | `render_email_html` → mailer `body_html` | `send_digest(site_url=…)` | ✓ WIRED | Parity unit green this pass |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Material modal body | `item.body_markdown` | GET `/admin/shortlist` materials join (live) or mock shortlist | Yes | ✓ FLOWING |
| Material counts | `char_count` / `word_count` | `material_counts(body_markdown)` | Yes | ✓ FLOWING |
| Email iframe | `emailModal.preview.html` | POST preview → `render_email_html` on the live path | Yes | ✓ FLOWING |
| Send HTML | `body_html` | Same `render_email_html` as preview | Yes | ✓ FLOWING |
| Long-body seam | `items[0].body_markdown` | `__DIGEST_ADMIN_MATERIAL_LONG_BODY__` inside `useMocks()` only | Test seam; live fetch unchanged | ✓ FLOWING |
| Ban scrub | materials text columns | Migration 010 on shared VM | Yes (runbook Applied + empty title probe) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full-item shortlist DTO | `uv run pytest tests/unit/test_http_admin.py::test_admin_shortlist_returns_full_items -q` | 7 passed in the combined named run (0.97s) | ✓ PASS |
| Interstitial `\n\n` → `<p>` | `…::test_render_interstitial_html_two_paragraphs_via_blank_line` | included in the 7 passed | ✓ PASS |
| Preview HTML composition | `…::test_preview_html_present_with_interstitial_paragraphs` | included in the 7 passed | ✓ PASS |
| Preview≡send HTML | `…::test_preview_email_html_matches_send_html` | included in the 7 passed | ✓ PASS |
| Ban list Python↔JS | `…::test_python_forbidden_lower_matches_js_mirror` | included in the 7 passed | ✓ PASS |
| No ban import in renderers | `…::test_email_render_module_does_not_import_or_call_ban_helper` | included in the 7 passed | ✓ PASS |
| Intro + material HTML | `…::test_render_email_html_applies_interstitial_to_intro_and_includes_material` | included in the 7 passed | ✓ PASS |
| Material close stays visible | `npx playwright test --project=web tests/admin.spec.js --grep "material preview close stays visible…"` | passed (2.2s) | ✓ PASS |
| Email close stays visible, `ul` count 0 | same Playwright invocation, email grep | passed (2.4s) | ✓ PASS |
| One approved article is in the iframe, not a light-DOM list | same Playwright invocation | passed (5.6s) | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| ADUX-01 | 13-01, 13-03, 13-07 | Material preview body/provenance/counts/reader link; close stays usable while the body scrolls | ✓ SATISFIED | Truths 1, 5, 6, 11, 14 |
| ADUX-02 | 13-02, 13-04, 13-06, 13-07, 13-08 | Real email HTML preview, send parity, pinned email close, no duplicate items list | ✓ SATISFIED | Truths 2, 7, 8, 12, 13 |
| ADUX-03 | 13-02, 13-04 | Interstitial paragraph breaks + UI hint | ✓ SATISFIED | Truths 3, 10, 15 |
| ADUX-04 | 13-02, 13-05 | No leaked test chrome after cleanup | ✓ SATISFIED | Truths 4, 9 |

REQUIREMENTS.md maps only ADUX-01, ADUX-02, ADUX-03, and ADUX-04 to Phase 13. Every ID declared on plans 13-01 through 13-08 is one of those four. No orphaned Phase 13 IDs.

### Prohibitions (judgment-tier — re-checked in code this pass)

| Statement | Verdict | Evidence |
| --------- | ------- | -------- |
| MUST NOT add `/admin/materials/:id` fetch for preview | satisfied | Admin router has no materials path; modal takes the shortlist item |
| MUST NOT weaken `AdminShortlistResponse` `extra=forbid` | satisfied | `ConfigDict(extra="forbid")` on the response and the item model |
| MUST NOT invent `body_markdown` when missing | satisfied | Nullable pass-through; empty UI copy |
| MUST NOT assemble email HTML in the SPA on the live path | satisfied | Live `previewEmail` returns `response.json()`; mock composer is inside `useMocks()` |
| MUST NOT strip ban tokens at render time | satisfied | `email_render.py` has no `email_chrome` import; unit green |
| MUST NOT put the issue URL into preview/send HTML | satisfied | Issue URL is only in the plain send wrapper |
| MUST NOT enable scriptable iframe sandbox flags | satisfied | `sandbox=""` |
| MUST NOT claim shared-VM cleanup without apply evidence | satisfied | Runbook §4g Applied 2026-10-03 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `web/src/pages/AdminDigestPage.jsx` | textarea | `placeholder` attribute | ℹ️ Info | Form placeholder, not a stub |
| — | — | No `TBD` / `FIXME` / `XXX` in the gap-closure files | — | Clean |

### Human Verification Required

None. The prior human checks that failed in UAT (close scrolling away; duplicate email list) are now covered by the Playwright tests run in this pass. The connecting-text hint check already passed UAT and the markup is unchanged.

### Gaps Summary

No open gaps. UAT G-13-1, G-13-2, G-13-3, and G-13-3b are closed in the current dialog shell and in the tests executed here. G-13-3c does not require a code change. The reader-page error is deferred to backlog phases 999.1 and 999.2.

---

_Verified: 2026-10-03T09:34:00Z_
_Verifier: Claude (gsd-verifier)_
