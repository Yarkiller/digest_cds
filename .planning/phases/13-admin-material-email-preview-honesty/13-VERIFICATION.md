---
phase: 13-admin-material-email-preview-honesty
verified: 2026-10-03T07:27:42Z
status: human_needed
score: 10/14 must-haves verified
covered_files:
  - .planning/phases/13-admin-material-email-preview-honesty/13-01-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-02-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-03-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-04-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-05-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-06-PLAN.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-01-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-02-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-03-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-04-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-05-SUMMARY.md
  - .planning/phases/13-admin-material-email-preview-honesty/13-06-SUMMARY.md
  - backend/src/backend/domain/shortlist.py
  - backend/src/backend/domain/email_chrome.py
  - backend/src/backend/application/use_cases/get_admin_shortlist.py
  - backend/src/backend/application/use_cases/email_render.py
  - backend/src/backend/application/use_cases/preview_digest_email.py
  - backend/src/backend/application/use_cases/send_digest.py
  - backend/src/backend/application/ports/mailer.py
  - backend/src/backend/composition/settings.py
  - backend/src/backend/infrastructure/stub_mailer.py
  - backend/src/backend/interface/http/routes/admin.py
  - backend/src/backend/tests_support/in_memory.py
  - supabase-integration/src/supabase_integration/shortlist_repository.py
  - supabase-integration/migrations/010_phase13_scrub_test_header.sql
  - web/src/pages/AdminDigestPage.jsx
  - web/src/services/adminApi.js
  - web/src/utils/forbiddenChrome.js
  - tests/unit/test_http_admin.py
  - tests/unit/test_email_render.py
  - tests/unit/test_preview_digest.py
  - tests/unit/test_send_digest.py
  - tests/admin.spec.js
  - docs/agents/local-platform-runbook.md
  - .env.example
  - .planning/phases/12-admin-shortlist-empty-batch-contract/12-FIX-01-LOCK.md
covered_digest: "v2:sha256:4360b6a8f05d7ca1986cf2fe4bb398fd923557ca3eddcab7a58aef97bf39d17f"
behavior_unverified: 0
overrides_applied: 0
decision_coverage:
  honored: 20
  total: 20
  not_honored: []
human_verification:
  - test: "Open /admin/digest as admin → Превью материала on a long-title / long-provenance item"
    expected: "Title and provenance wrap with break-words; close (✕) stays reachable"
    why_human: "PLAN backstop (verification: backstop) — CSS wrap/clip not proven by unit tests"
  - test: "Open material preview on a long body_markdown item; scroll the dialog"
    expected: "Body scrolls inside the dialog; close control remains usable"
    why_human: "PLAN backstop — scroll/clip interaction needs visual check"
  - test: "Open «Превью письма» with a long subject and multi-block HTML"
    expected: "Subject wraps; iframe/modal scrolls without clipping close"
    why_human: "PLAN backstop — iframe layout/overflow needs visual check"
  - test: "Type a long connecting-text with blank-line paragraphs; confirm hint visibility"
    expected: "Textarea wraps/scrolls; muted «Пустая строка = новый абзац» stays visible below"
    why_human: "PLAN backstop — editor UX not covered by automated asserts"
---

# Phase 13: Admin material & email preview honesty Verification Report

**Phase Goal:** Admin can inspect a real material body and a real email HTML preview before send
**Verified:** 2026-10-03T07:27:42Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ------- | ------ | -------------- |
| 1 | On `/admin/digest`, material preview shows `body_markdown`, `provenance_label`, char/word counts, and a working link to `/materials/<slug>` (not title+dek only) | ✓ VERIFIED | `AdminItemPreview` renders title → provenance → `~{char} символов · {word} слов · ~{min} мин` → Markdown body → `Открыть материал →` (`AdminDigestPage.jsx`). DTO fields from `AdminShortlistItemResponse`. Named unit `test_admin_shortlist_returns_full_items` **PASS**. Playwright case `material preview shows body_markdown provenance counts and reader link` present |
| 2 | «Превью письма» renders real email HTML including intro, summaries, and links (not titles-only) | ✓ VERIFIED | Backend `render_email_html` → `DigestPreviewResponse.html`; FE iframe `data-testid=email-preview-frame` `sandbox=""` `srcDoc={preview.html}`. Live `previewEmail` returns `response.json()` (API html). Unit `test_render_email_html_applies_interstitial_to_intro_and_includes_material` **PASS** |
| 3 | Interstitial connecting text preserves paragraph breaks so `\n\n` is visible as whitespace / separate paragraphs | ✓ VERIFIED | `render_interstitial_html`: strip → escape → `\n\n`→`<p>` → `\n`→`<br>`. Unit `test_render_interstitial_html_two_paragraphs_via_blank_line` **PASS** (`one\n\ntwo` → `<p>one</p><p>two</p>`). Preview unit `test_preview_html_present_with_interstitial_paragraphs` **PASS** |
| 4 | Leaked `test-header` (and equivalent seed/test chrome) does not appear on admin preview surfaces after cleanup | ✓ VERIFIED | Migration `010_phase13_scrub_test_header.sql` checked in; runbook **§4g** Applied 2026-10-03 Studio; PostgREST `materials title ilike %test-header%` → `[]` (verifier re-probe). `FORBIDDEN_LOWER` Python↔JS sync unit **PASS**. Playwright ban-surface asserts present. Renderers do not import ban helper (unit **PASS**) |
| 5 | GET `/admin/shortlist` enrichment uses ShortlistRepository join only — required keys `body_markdown`, `provenance_label`, `slug`, `reading_minutes`, `char_count`, `word_count`; `extra=forbid` retained | ✓ VERIFIED | `shortlist_repository.py` select `materials(...,body_markdown,slug,provenance_label,reading_minutes)`; `material_counts` via `len`/`str.split()`; `AdminShortlistResponse`/`Item` `ConfigDict(extra="forbid")`. No `/admin/materials/:id` route for preview |
| 6 | Material modal uses enriched shortlist DTO only (no fetch-on-open); markdown stack + honest empty body | ✓ VERIFIED | `AdminItemPreview({ item })` — no fetch; `Markdown` + `remarkGfm` + `rehypeSanitize` + `rehypeSlug`. Empty → «Текст материала недоступен». Playwright empty-body case present; request spy expects zero `/admin/materials/` hits |
| 7 | Email preview surface is sandboxed backend `html` via iframe; FE does not invent live HTML; loading/error honest | ✓ VERIFIED | iframe `sandbox=""` + `srcDoc`; mock path may compose HTML for Playwright only (`composeMockPreviewHtml` documented mock-only). Loading «Загрузка…» / error «Превью недоступно» + «Повторить превью» |
| 8 | `send_digest` uses same `render_email_html` + trusted `Settings.site_url` as preview (D-12 parity) | ✓ VERIFIED | Both routes pass `request.app.state.settings.site_url`. Named unit `test_preview_email_html_matches_send_html` **PASS**. Issue URL only in plain send wrapper (`send_digest.py`), not in `render_email_html` |
| 9 | Ban helpers assert-only; Python/JS lists identical; scrub migration + shared-VM apply evidence (ADUX-04) | ✓ VERIFIED | `email_chrome.py` ↔ `forbiddenChrome.js` three tokens; `test_python_forbidden_lower_matches_js_mirror` **PASS**; `test_email_render_module_does_not_import_or_call_ban_helper` **PASS**; §4g Applied line + empty probe |
| 10 | Connecting-text / intro show muted hint «Пустая строка = новый абзац» (ADUX-03 UI) | ✓ VERIFIED | Two hint spans in `AdminDigestPage.jsx`; Playwright `Пустая строка = новый абзац hint under intro and connecting text` present |
| 11 | Long titles and provenance wrap with `break-words` in the material modal | ⚠️ insufficient_spec | `break-words` classes present; PLAN `verification: backstop` — no automated visual proof → Human Verification |
| 12 | Long material markdown scrolls inside the material preview dialog without clipping the close control | ⚠️ insufficient_spec | `max-h-[90vh] overflow-y-auto` present; PLAN backstop → Human Verification |
| 13 | Long email subject wraps; long HTML scrolls via modal/iframe without clipping the close control | ⚠️ insufficient_spec | `break-words` on subject + scrollable modal/iframe; PLAN backstop → Human Verification |
| 14 | Long connecting text wraps/scrolls in the textarea; hint remains visible below | ⚠️ insufficient_spec | Hint markup present; PLAN backstop → Human Verification |

**Score:** 10/14 truths verified (0 present, behavior-unverified; 4 backstop → human)

### Decision Coverage

All trackable CONTEXT.md decisions are honored by shipped artifacts. (20/20 honored; non-blocking gate)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `tests/unit/test_http_admin.py` | Full-item DTO proof | ✓ VERIFIED | `test_admin_shortlist_returns_full_items` green; `gsd verify.artifacts` 13-01 4/4 |
| `backend/.../domain/shortlist.py` | ShortlistItem + counts | ✓ VERIFIED | `material_counts` + AdminShortlistItem fields |
| `supabase-integration/.../shortlist_repository.py` | Widened materials select | ✓ VERIFIED | Join includes body/slug/provenance/reading_minutes |
| `backend/.../email_render.py` | Shared HTML renderers | ✓ VERIFIED | interstitial + material block + compose |
| `tests/unit/test_email_render.py` | Interstitial/ban coverage | ✓ VERIFIED | Paragraph matrix + ban sync + no-import guard |
| `backend/.../preview_digest_email.py` | Preview html + plain honesty | ✓ VERIFIED | Calls `render_email_html` |
| `backend/.../domain/email_chrome.py` | FORBIDDEN_LOWER assert-only | ✓ VERIFIED | Three closed tokens |
| `web/src/pages/AdminDigestPage.jsx` | Material modal + email iframe | ✓ VERIFIED | AdminItemPreview + AdminEmailPreview |
| `web/src/services/adminApi.js` | Typed shortlist + preview html | ✓ VERIFIED | Live path `response.json()`; mocks for e2e |
| `tests/admin.spec.js` | Playwright honesty + ban asserts | ✓ VERIFIED | Material/email/ban/hint describes present |
| `backend/.../send_digest.py` | Shared render on send | ✓ VERIFIED | `render_email_html` + `body_html` to mailer |
| `backend/.../routes/admin.py` | Preview/send site_url wire | ✓ VERIFIED | Both POSTs pass trusted Settings |
| `tests/unit/test_preview_digest.py` | D-12 parity proof | ✓ VERIFIED | `test_preview_email_html_matches_send_html` green |
| `backend/.../stub_mailer.py` | `last_body_html` | ✓ VERIFIED | Optional capture |
| `010_phase13_scrub_test_header.sql` | Idempotent scrub | ✓ VERIFIED | Exists; closed-token UPDATE |
| `docs/agents/local-platform-runbook.md` | Apply/verify scrub | ✓ VERIFIED | **§4g** (plan text said §4f; §4f already used — intentional renumber per 13-05-SUMMARY) |
| `web/src/utils/forbiddenChrome.js` | JS ban mirror | ✓ VERIFIED | Synced list + `containsForbiddenChrome` |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | ------ | ------- | ------- |
| `materials(body_markdown,…)` join | `AdminShortlistItemResponse` JSON | `ShortlistRepository.get_current_batch` → `get_admin_shortlist` → `_to_response` | ✓ WIRED | Automated `verify.key-links` N/A (non-file `from`); manual grep confirms select → domain → HTTP fields |
| `compose_digest_segments` + `Settings.site_url` | `DigestEmailPreview.html` | `render_email_html` in `preview_digest_email` | ✓ WIRED | Preview route sets `html=preview.html` |
| `AdminShortlistItem.body_markdown` | `AdminItemPreview` Markdown | Shortlist DTO already on page | ✓ WIRED | No second network call on modal open |
| `POST /admin/shortlist/preview` `html` | iframe `srcDoc` | `adminApi.previewEmail` → AdminEmailPreview | ✓ WIRED | `data-testid=email-preview-frame` |
| `010` scrub SQL | Clean admin preview surfaces | Operator §4g apply + regression asserts | ✓ WIRED | Applied evidence + empty probe + unit/Playwright asserts |
| `settings.site_url` (send POST) | `render_email_html` → StubMailer `body_html` | `send_digest(site_url=…)` | ✓ WIRED | Parity unit proves preview≡send HTML |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Material modal body | `item.body_markdown` | GET `/admin/shortlist` → materials join → DTO | Yes (DB/mock shortlist item) | ✓ FLOWING |
| Material counts | `char_count` / `word_count` | `material_counts(body_markdown)` in use-case | Yes (computed from body) | ✓ FLOWING |
| Email iframe | `emailModal.preview.html` | POST preview → `render_email_html` (live) or mock composer | Yes (backend HTML on live path) | ✓ FLOWING |
| Send HTML | `body_html` | Same `render_email_html` as preview | Yes (parity unit) | ✓ FLOWING |
| Ban scrub | materials text columns | Migration 010 on shared VM | Yes (defensive UPDATE; probe empty) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------- |
| Full-item shortlist DTO | `uv run pytest …::test_admin_shortlist_returns_full_items -q` | passed | ✓ PASS |
| Interstitial `\n\n` → `<p>` | `…::test_render_interstitial_html_two_paragraphs_via_blank_line` | passed | ✓ PASS |
| Preview HTML composition | `…::test_preview_html_present_with_interstitial_paragraphs` | passed | ✓ PASS |
| Preview≡send HTML | `…::test_preview_email_html_matches_send_html` | passed | ✓ PASS |
| Ban list Python↔JS | `…::test_python_forbidden_lower_matches_js_mirror` | passed | ✓ PASS |
| No ban import in renderers | `…::test_email_render_module_does_not_import_or_call_ban_helper` | passed | ✓ PASS |
| Intro+material HTML | `…::test_render_email_html_applies_interstitial_to_intro_and_includes_material` | passed | ✓ PASS |
| Playwright admin honesty suite | (not re-run — needs browser; tests enumerated in `tests/admin.spec.js`) | existence only | ? SKIP |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------- |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| ADUX-01 | 13-01, 13-03 | Material preview body/provenance/counts/reader link | ✓ SATISFIED | Truths 1,5,6; REQUIREMENTS.md Phase 13 Complete |
| ADUX-02 | 13-02, 13-04, 13-06 | Real email HTML preview (+ send parity) | ✓ SATISFIED | Truths 2,7,8 |
| ADUX-03 | 13-02, 13-04 | Interstitial paragraph breaks + UI hint | ✓ SATISFIED | Truths 3,10 |
| ADUX-04 | 13-02, 13-05 | No leaked test chrome after cleanup | ✓ SATISFIED | Truth 4,9; migration Applied |

No orphaned Phase 13 requirement IDs in REQUIREMENTS.md beyond ADUX-01…04.

### Prohibitions (judgment-tier — LLM-judged, human review recommended)

| Statement | Verdict | Evidence |
| --------- | ------- | -------- |
| MUST NOT add `/admin/materials/:id` fetch for preview | satisfied | No such route; Playwright request spy asserts empty hits |
| MUST NOT weaken `AdminShortlistResponse` `extra=forbid` | satisfied | Still `ConfigDict(extra="forbid")` |
| MUST NOT invent `body_markdown` when missing | satisfied | Nullable pass-through; empty UI copy |
| MUST NOT construct/assemble email HTML in SPA (live) | satisfied | Live path returns API JSON; mock-only composer documented |
| MUST NOT strip ban tokens at render time | satisfied | `email_render` free of `email_chrome` import |
| MUST NOT put issue URL into preview/send HTML | satisfied | Issue URL only in plain send wrapper |
| MUST NOT enable scriptable iframe sandbox flags | satisfied | `sandbox=""` empty string |
| MUST NOT claim shared-VM cleanup without apply evidence | satisfied | Runbook §4g Applied 2026-10-03 + empty probe |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `web/src/pages/AdminDigestPage.jsx` | ~597 | `placeholder=` on textarea | ℹ️ Info | Form placeholder attribute — not a stub |
| — | — | No `TBD`/`FIXME`/`XXX` in phase impl files | — | Clean |

### Code-review disposition (non-blocking)

Per `13-REVIEW-DISPOSITION.md`: **CR-01** (publish order vs blocks when both `material_ids` and `blocks` sent) dispositioned **backlog** — SPA always derives matching orders from `issueBlocks`; not required for Phase 13 verify. WR-01…04 / IN-01…03 also backlog. No verify blockers from review.

### Human Verification Required

### 1. Long title / provenance wrap

**Test:** Open material preview on an item with a long title and long provenance  
**Expected:** Text wraps (`break-words`); close control remains usable  
**Why human:** PLAN `verification: backstop`

### 2. Long markdown scroll

**Test:** Open material preview with long `body_markdown`; scroll  
**Expected:** Body scrolls in dialog; close not clipped  
**Why human:** PLAN backstop

### 3. Long email subject / HTML scroll

**Test:** Open «Превью письма» with long subject and multi-block HTML  
**Expected:** Subject wraps; modal/iframe scrolls; close usable  
**Why human:** PLAN backstop

### 4. Long connecting text + hint

**Test:** Enter long connecting text with `\n\n` paragraphs  
**Expected:** Textarea wraps/scrolls; «Пустая строка = новый абзац» remains visible  
**Why human:** PLAN backstop

### Gaps Summary

No automated gaps against the four ROADMAP success criteria or ADUX-01…04. Phase status is `human_needed` solely because four PLAN UI backstops require visual confirmation. CR-01 remains backlog (SPA path honest).

---

_Verified: 2026-10-03T07:27:42Z_
_Verifier: Claude (gsd-verifier)_
