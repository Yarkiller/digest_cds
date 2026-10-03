---
phase: 13-admin-material-email-preview-honesty
verified: 2026-10-03T21:20:00Z
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
covered_digest: "v2:sha256:a9f8ccf43cf5b1fa19c4ba4046cee65aab5e5a92144aeeb2013e8b8dd2caca19"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 15/15
  gaps_closed: []
  gaps_remaining: []
  regressions: []
deferred:
  - truth: "Reader page at /materials/<slug> loads without an error when opened from the admin preview link"
    addressed_in: "Phase 999.1 and Phase 999.2"
    evidence: "ROADMAP backlog: reader /materials/<slug> error page is filed as not Phase 13 scope (UAT O3). Phase 13 proves the href /materials/<slug>."
advisory: []
---

# Phase 13: Admin material & email preview honesty Verification Report

**Phase Goal:** Admin can inspect a real material body and a real email HTML preview before send
**Verified:** 2026-10-03T21:20:00Z
**Status:** passed
**Re-verification:** Yes — **stale re-verification (GSD #4682)**. The prior report's `covered_digest` (`v2:sha256:6e0d39f8…)` no longer matches the current source tree because Phase 14 edited several covered files after that verifier ran (`web/src/pages/AdminDigestPage.jsx`, `web/src/services/adminApi.js`, `tests/admin.spec.js`, `backend/src/backend/interface/http/routes/admin.py`, `backend/src/backend/domain/shortlist.py`, `tests/unit/test_http_admin.py`). This report was regenerated from the **current** codebase — all truths were re-checked against live source and re-run tests, then a fresh digest was written.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ------- | ------ | -------------- |
| 1 | On `/admin/digest`, material preview shows `body_markdown`, `provenance_label`, char/word counts, and a link to `/materials/<slug>` (not title+dek only) | ✓ VERIFIED | `AdminItemPreview` renders title → optional provenance → `~{charCount} символов · {wordCount} слов · ~{readingMinutes} мин` → sanitized Markdown body → `Открыть материал →` (`AdminDigestPage.jsx` 941–1001). Playwright `material preview shows body_markdown provenance counts and reader link` **PASS** this pass (asserts body text, `YouTube · lecture`, `~128 символов · 18 слов · ~2 мин`, href `/materials/building-production-rag-systems`) |
| 2 | «Превью письма» renders real email HTML including intro, summaries, and links (not titles-only) | ✓ VERIFIED | `render_email_html` emits intro `<p>`, material `<h2>`, optional dek, and `Читать →` absolute link (`email_render.py`). Live `previewEmail` returns `response.json()`; iframe `sandbox=""` `srcDoc={preview.html}` (`AdminDigestPage.jsx` 869–877). Playwright `email-preview-frame shows sandboxed backend HTML with material title` **PASS** (title read from iframe heading, `Читать →` link visible) |
| 3 | Interstitial connecting text preserves paragraph breaks so `\n\n` is visible as separate paragraphs | ✓ VERIFIED | `render_interstitial_html` strips → escapes → splits `\n\n` into `<p>` and single `\n` into `<br>`; applied to intro and `kind=text` blocks (`email_render.py` 14–70). Unit `test_render_interstitial_html_two_paragraphs_via_blank_line` and `test_preview_html_present_with_interstitial_paragraphs` **PASS** in the full suite this pass |
| 4 | Leaked `test-header` (and equivalent seed/test chrome) does not appear on admin preview surfaces after cleanup | ✓ VERIFIED | Migration `010_phase13_scrub_test_header.sql` checked in; runbook §4g **Applied 2026-10-03** with empty PostgREST `title ilike %test-header%` probe. Two Playwright ban-surface tests **PASS** this pass (material modal text + iframe srcdoc/frame text). Unit `test_python_forbidden_lower_matches_js_mirror` and `test_email_render_module_does_not_import_or_call_ban_helper` **PASS** |
| 5 | GET `/admin/shortlist` enrichment uses the materials join only — keys `body_markdown`, `provenance_label`, `slug`, `reading_minutes`, `char_count`, `word_count`; `extra=forbid` retained | ✓ VERIFIED | `shortlist_repository.py` select includes those columns (221–222) and maps them in `_item_from_row`; `AdminShortlistItemResponse`/`AdminShortlistResponse` keep `ConfigDict(extra="forbid")` and declare all six fields (`admin.py` 40–60). Named unit `test_admin_shortlist_returns_full_items` **PASS** |
| 6 | Material modal uses the enriched shortlist DTO only (no fetch-on-open); markdown stack + honest empty body | ✓ VERIFIED | `AdminItemPreview({ item })` — no fetch; `Markdown` + `remarkGfm` + `rehypeSlug` + `rehypeSanitize`. Empty body copy «Текст материала недоступен». Playwright request spy asserts zero `/admin/materials/` hits; empty-body case **PASS** both this pass |
| 7 | Email preview surface is sandboxed backend `html` via iframe; the live SPA does not invent HTML; loading/error copy is honest | ✓ VERIFIED | iframe `sandbox=""` + `srcDoc`; `composeMockPreviewHtml` runs only inside `previewEmail`'s `useMocks()` branch (`adminApi.js` 469–552). Loading «Загрузка…» / error «Превью недоступно» + «Повторить превью» under the pinned header. Playwright iframe case **PASS** |
| 8 | `send_digest` uses the same `render_email_html` + trusted `Settings.site_url` as preview | ✓ VERIFIED | `send_digest.py` calls `render_email_html(..., site_url=site_url)` (171–174); both admin POSTs pass `request.app.state.settings.site_url` (`admin.py` 387, 444). Named unit `test_preview_email_html_matches_send_html` **PASS**; issue URL is only in the plain send wrapper, never in HTML |
| 9 | Ban helpers are assert-only; Python and JS lists match; scrub migration + shared-VM apply evidence remain (ADUX-04) | ✓ VERIFIED | `email_chrome.py` `FORBIDDEN_LOWER = ["test-header","test_header","testheader"]` ↔ `forbiddenChrome.js` identical; `email_render.py` has no ban import. Unit sync + source-guard tests **PASS**. §4g Applied line present and unchanged |
| 10 | Connecting-text and intro show muted hint «Пустая строка = новый абзац» | ✓ VERIFIED | Two hint spans in `AdminDigestPage.jsx` (intro 601, issue text block 645). Playwright `Пустая строка = новый абзац hint under intro and connecting text` **PASS** this pass (and asserts no `role=toolbar` markup toolbar) |
| 11 | On the material preview dialog, «Закрыть» stays in view while the markdown body scrolls, uses `cursor-pointer`, and the header row is outside `overflow-y-auto` (G-13-1, G-13-2) | ✓ VERIFIED | Shell `flex` / `max-h-[90vh]` / `overflow-hidden`; header `shrink-0`; scroll region `min-h-0 flex-1 overflow-y-auto`; close `cursor-pointer` (952–971). Playwright `material preview close stays visible while the body scrolls` **PASS** this pass (`insideOverflow` false, `hasPointer` true, `scrollHeight > clientHeight`, close in viewport) |
| 12 | On the email preview dialog, the same close control stays in view while subject and iframe scroll, and uses `cursor-pointer` (G-13-3) | ✓ VERIFIED | Same shell on the email dialog (832–846). Playwright `email preview close stays visible while the preview scrolls` **PASS** this pass at 1280×400 (`ul` count 0, close in viewport, scroll region overflows) |
| 13 | Successful email preview shows the subject and the sandboxed iframe only; no numbered `preview.items` list and no `preview.body` node (G-13-3b) | ✓ VERIFIED | Success branch renders subject + `email-preview-frame` only; no `preview.items` map, no `preview.body`/`email-preview-body` in `AdminDigestPage.jsx` (867–880). No `emailDialog.locator("li")` remains in `tests/admin.spec.js`. Playwright one-article + close-scroll cases **PASS** with dialog `ul` count 0 |
| 14 | Long titles and provenance wrap with `break-words` in the material modal | ✓ VERIFIED | `break-words` on title (972) and provenance (975) inside the scroll region. UAT test 1 reported pass; markup unchanged by gap closure/Phase 14 |
| 15 | Long connecting text wraps in the textarea; the hint stays visible below | ✓ VERIFIED | Intro textarea keeps the hint as the next sibling (601); native textarea wrap. UAT test 4 reported pass; markup unchanged |

**Score:** 15/15 truths verified (0 present, behavior-unverified)

UAT G-13-3c (single connecting line looks flat in the iframe) is not a markup defect. `render_interstitial_html("hello")` is one `<p>hello</p>`; only `\n\n` splits paragraphs (truth 3, unit-tested this pass).

### Deferred Items

Items not yet met but explicitly addressed in later milestone phases.

| # | Item | Addressed In | Evidence |
| --- | ------ | ------------- | ---------- |
| 1 | Reader `/materials/<slug>` returns an error page when the admin link is opened | Phase 999.1 and Phase 999.2 | ROADMAP backlog follow-ups from UAT O3. Phase 13's contract is the href on the preview link, which the Playwright material case asserts |

### Advisory (New Scope, Unevidenced)

None. Re-verification scanned the covered source files (including Phase 14 edits to `AdminDigestPage.jsx`, `adminApi.js`, `admin.spec.js`). No new-scope blocker without deterministic evidence.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `tests/unit/test_http_admin.py` | Full-item DTO proof | ✓ VERIFIED | `test_admin_shortlist_returns_full_items` green this pass |
| `backend/.../domain/shortlist.py` | ShortlistItem + counts | ✓ VERIFIED | `material_counts` present; additive fields on both models |
| `supabase-integration/.../shortlist_repository.py` | Widened materials select | ✓ VERIFIED | Join includes body, slug, provenance, reading_minutes |
| `backend/.../email_render.py` | Shared HTML renderers | ✓ VERIFIED | interstitial + material block + compose |
| `tests/unit/test_email_render.py` | Interstitial and ban coverage | ✓ VERIFIED | Paragraph and ban-sync tests green this pass |
| `backend/.../preview_digest_email.py` | Preview html | ✓ VERIFIED | Calls `render_email_html`, additive `html` on DTO |
| `backend/.../domain/email_chrome.py` | FORBIDDEN_LOWER assert-only | ✓ VERIFIED | Not imported by `email_render.py` |
| `web/src/pages/AdminDigestPage.jsx` | Pinned dialogs + iframe, no items list | ✓ VERIFIED | Header outside scrollport; success branch is subject + iframe |
| `web/src/services/adminApi.js` | Live JSON preview; mock-only long body | ✓ VERIFIED | `__DIGEST_ADMIN_MATERIAL_LONG_BODY__` only inside `useMocks()` (259/269) |
| `tests/admin.spec.js` | Close-scroll and list-removal proofs | ✓ VERIFIED | Nine named Playwright tests green this pass |
| `backend/.../send_digest.py` | Shared render on send | ✓ VERIFIED | `render_email_html` + plain issue URL wrapper |
| `backend/.../routes/admin.py` | Preview/send `site_url` wire | ✓ VERIFIED | Both POSTs pass trusted Settings; `html: str` on preview DTO |
| `tests/unit/test_preview_digest.py` | Preview≡send HTML | ✓ VERIFIED | `test_preview_email_html_matches_send_html` green this pass |
| `010_phase13_scrub_test_header.sql` | Idempotent scrub | ✓ VERIFIED | File present; apply recorded in runbook §4g |
| `docs/agents/local-platform-runbook.md` | Apply/verify scrub | ✓ VERIFIED | §4g Applied 2026-10-03 (plan said §4f, which was already occupied — naming deviation only) |
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
| `010` scrub SQL | Clean admin preview surfaces | Operator §4g apply + regression asserts | ✓ WIRED | Applied evidence unchanged; ban units + Playwright green |
| `settings.site_url` (send POST) | `render_email_html` → mailer `body_html` | `send_digest(site_url=…)` | ✓ WIRED | Parity unit green this pass |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Material modal body | `item.body_markdown` | GET `/admin/shortlist` materials join (live) or mock shortlist | Yes | ✓ FLOWING |
| Material counts | `char_count` / `word_count` | `material_counts(body_markdown)` | Yes | ✓ FLOWING |
| Email iframe | `emailModal.preview.html` | POST preview → `render_email_html` on the live path | Yes | ✓ FLOWING |
| Send HTML | `body_html` | Same `render_email_html` as preview | Yes | ✓ FLOWING |
| Long-body seam | `items[0].body_markdown` | `__DIGEST_ADMIN_MATERIAL_LONG_BODY__` inside `useMocks()` only | Test seam; live fetch unchanged | ✓ FLOWING |
| Ban scrub | materials text columns | Migration 010 on shared VM | Yes (runbook Applied + empty probe) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full backend suite (all Phase 13 unit proofs) | `uv run pytest -q` | `684 passed, 1 warning in 5.97s` | ✓ PASS |
| Phase 13 admin E2E suite (9 tests) | `npx playwright test --project=web tests/admin.spec.js --grep "material preview\|email preview close\|email-preview-frame\|Пустая строка\|preview lists one approved-ready\|forbidden chrome tokens"` | `9 passed (26.4s)` | ✓ PASS |

The 9 Playwright cases executed this pass: `preview lists one approved-ready article`, `Пустая строка = новый абзац hint`, `email-preview-frame shows sandboxed backend HTML with material title`, `email preview close stays visible while the preview scrolls`, `material modal text has no forbidden chrome tokens`, `email-preview-frame content has no forbidden chrome tokens`, `material preview shows body_markdown provenance counts and reader link`, `material preview empty body shows Текст материала недоступен without toast`, `material preview close stays visible while the body scrolls`.

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

### Decision Coverage

All trackable CONTEXT.md decisions are honored by shipped artifacts. (20/20 decisions honored; `check.decision-coverage-verify` → `{total: 20, honored: 20, not_honored: []}`.)

### Prohibitions (judgment-tier — re-checked in code this pass)

| Statement | Verdict | Evidence |
| --------- | ------- | -------- |
| MUST NOT add `/admin/materials/:id` fetch for preview | satisfied | Admin router exposes only shortlist/preview/send + Phase 14 `POST /materials/ready` routes; no materials-by-id GET; modal takes the shortlist item |
| MUST NOT weaken `AdminShortlistResponse` `extra=forbid` | satisfied | `ConfigDict(extra="forbid")` on the response and the item model |
| MUST NOT invent `body_markdown` when missing | satisfied | Nullable pass-through; empty UI copy «Текст материала недоступен» |
| MUST NOT assemble email HTML in the SPA on the live path | satisfied | Live `previewEmail` returns `response.json()`; mock composer is inside `useMocks()` |
| MUST NOT strip ban tokens at render time | satisfied | `email_render.py` has no `email_chrome` import; source-guard unit green |
| MUST NOT put the issue URL into preview/send HTML | satisfied | Issue URL is only in the plain send wrapper |
| MUST NOT enable scriptable iframe sandbox flags | satisfied | `sandbox=""` |
| MUST NOT claim shared-VM cleanup without apply evidence | satisfied | Runbook §4g Applied 2026-10-03 + empty PostgREST probe |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `web/src/pages/AdminDigestPage.jsx` | textarea | `placeholder` attribute | ℹ️ Info | Form placeholder, not a stub |
| — | — | No `TBD` / `FIXME` / `XXX` in the covered files | — | Clean (scanned this pass) |

### Human Verification Required

None. The UAT observations that previously failed (close scrolling away; duplicate email list) are covered by the Playwright tests run in this pass; the backstop long-text items are covered by UAT passes plus `break-words`/textarea evidence. No behavior-dependent truth is left without a passing test.

### Gaps Summary

No open gaps. UAT G-13-1, G-13-2, G-13-3, and G-13-3b are closed in the current dialog shell and in the tests executed here. G-13-3c does not require a code change. The reader-page error is deferred to backlog phases 999.1 and 999.2. The runbook section landed as §4g (not the plan's §4f, which already documented admin shortlist/send E2E) — a naming deviation that preserves the required apply/verify contract.

---

_Verified: 2026-10-03T21:20:00Z_
_Verifier: Claude (gsd-verifier)_
