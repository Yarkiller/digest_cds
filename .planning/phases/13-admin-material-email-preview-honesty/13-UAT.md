---
status: diagnosed
phase: 13-admin-material-email-preview-honesty
source: [13-VERIFICATION.md]
started: 2026-10-03T07:30:00Z
updated: 2026-10-03T08:40:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Long title / provenance wrap
expected: Title and provenance wrap with break-words; close (✕) stays reachable
result: issue
reported: "pass with 2 observations (O1 close sticky, O2 cursor pointer). O1+O2 Phase 13 fix: Modal close position sticky (top-right within modal); CSS cursor: pointer on close; retest long markdown scroll → close visible at all times."
severity: major

### 2. Long markdown scroll
expected: Body scrolls inside the material preview dialog; close control remains usable
result: issue
reported: "Body scrolls inside dialog: pass. Close control remains usable: fail. Close (✕) is not sticky — scrolls away with content. To close after reading mid-document, user must scroll back to top. Same root cause as O1 from Test 1. Fix: position sticky/fixed for close button within modal header. After fix — retest Test 1 + Test 2."
severity: blocker

### 3. Long email subject / HTML scroll
expected: Subject wraps; iframe/modal scrolls without clipping close
result: issue
reported: "fail (2 bugs + minor verify). Bug 1: ✕ scrolls away (same as T1/T2) — sticky close in modal header. Bug 2 NEW: duplicate numbered plain-text list below iframe duplicates HTML email; body must not render in UI (Phase 13 lock) — hide plain body; optional HTML/Plain toggle default HTML. Bug 3 minor: interstitial «Связывающий текст - тест» flat in iframe, should be <p> per ADUX-03 — verify Phase 12 interstitial_html. Retest 1, 2, 3 after fixes."
severity: blocker

### 4. Long connecting text + hint
expected: Textarea wraps/scrolls; muted «Пустая строка = новый абзац» stays visible below
result: pass

## Summary

total: 4
passed: 1
issues: 3
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-13-1
  truth: "Material preview modal close (✕) stays sticky top-right within the modal at all scroll positions, and uses CSS cursor: pointer"
  status: failed
  reason: "User reported (pass observations O1+O2): Modal close needs position sticky (top-right fixed within modal); CSS cursor: pointer on close button; retest with long markdown body scroll → close visible at all times"
  severity: major
  test: 1
  root_cause: "AdminItemPreview puts ✕ inside the dialog scrollport (max-h-[90vh] overflow-y-auto) as a non-sticky flex item, and the button has no cursor-pointer (Tailwind v4 preflight does not set button cursor)."
  artifacts:
    - path: web/src/pages/AdminDigestPage.jsx
      issue: "close button at ~915-927 is inside overflow-y-auto with no sticky/fixed and no cursor-pointer"
  missing:
    - "Pin the material-preview header or close control (sticky top-0 or header outside the scrollport)"
    - "Add cursor-pointer on the close button"
  debug_session: .planning/debug/modal-close-not-sticky.md

- gap_id: G-13-2
  truth: "Body scrolls inside the material preview dialog; close control remains usable (sticky/fixed within modal header so it never scrolls away)"
  status: failed
  reason: "User reported: Body scrolls inside dialog: pass. Close control remains usable: fail. Close (✕) is not sticky — scrolls away with content. To close after reading mid-document, user must scroll back to top. Same root cause as O1 from Test 1. Fix: position sticky/fixed for close button within modal header. After fix — retest Test 1 + Test 2."
  severity: blocker
  test: 2
  root_cause: "Same AdminItemPreview scrollport as G-13-1: overflow-y-auto scrolls the close control off with the markdown body."
  artifacts:
    - path: web/src/pages/AdminDigestPage.jsx
      issue: "body and close share one scrollport (~915-946)"
  missing:
    - "Keep close in a non-scrolling or sticky header while the body keeps scrolling"
  debug_session: .planning/debug/modal-close-not-sticky.md

- gap_id: G-13-3
  truth: "Email preview modal close (✕) stays sticky in modal header; does not scroll away with content"
  status: failed
  reason: "User reported Bug 1 (O1 повтор): ✕ scrolls away with modal content; user must scroll back to close. Same root cause as Test 1 + Test 2. Fix: sticky close in modal header."
  severity: blocker
  test: 3
  root_cause: "Email preview copies the same scrolling panel; ✕ scrolls away with subject, iframe, and item list."
  artifacts:
    - path: web/src/pages/AdminDigestPage.jsx
      issue: "email dialog close at ~785-797 is inside overflow-y-auto"
  missing:
    - "Sticky close in the email modal header (same pattern as material preview)"
  debug_session: .planning/debug/modal-close-not-sticky.md

- gap_id: G-13-3b
  truth: "Email preview modal shows HTML in iframe only; plain `body` is internal (stub logs, text clients, debug) and must not render as a duplicate numbered list under the iframe"
  status: failed
  reason: "User reported Bug 2 NEW: Under the iframe, modal renders a numbered plain-text list duplicating HTML email content. Violates Phase 13 lock that body is internal. Visual clutter. Fix: hide plain body in modal; optional HTML/Plain toggle default HTML."
  severity: major
  test: 3
  root_cause: "The visible duplicate is not preview.body. The success branch always renders emailModal.preview.items as {rank}. {title} under the iframe. preview.body stays on the DTO and is not mounted."
  artifacts:
    - path: web/src/pages/AdminDigestPage.jsx
      issue: "ul at ~832-838 maps preview.items under the iframe"
    - path: web/src/services/adminPreviewComposition.js
      issue: "composePreviewItems sets 1-based rank used by that list"
  missing:
    - "Do not render the items ul on the user-visible email preview (iframe plus subject only)"
  debug_session: .planning/debug/email-plain-body-rendered.md

- gap_id: G-13-3c
  truth: "Interstitial connecting text in email HTML renders as paragraph (<p>) per ADUX-03 / Phase 12 interstitial_html contract"
  status: failed
  reason: "User reported Bug 3 (minor, verify): «Связывающий текст - тест» renders flat inside iframe; should be <p>. Verify against Phase 12 interstitial_html render; fix if mismatch."
  severity: minor
  test: 3
  root_cause: "Not a markup defect. render_interstitial_html already wraps connecting text in <p>. A single line with no blank line is one paragraph in an unstyled iframe srcdoc, so it looks flat. No code change."
  artifacts:
    - path: backend/src/backend/application/use_cases/email_render.py
      issue: "already emits <p> per D-13; flat look is unstyled srcdoc, not a missing tag"
  missing: []
  debug_session: .planning/debug/interstitial-not-paragraph.md

## Deferred Follow-Ups

- test: 1
  idea: "O3 — Reader /materials/<slug> returns error page. Check: slug validity, reader endpoint health, SPA route. Not Phase 13 scope. File for Phase 14 / debug session."
  deferred_at: 2026-10-03

- test: 3
  idea: "O3 — «Открыть материал →» from email/admin preview leads to error page. Reader /materials/<slug> route issue, not admin preview. Separate ticket."
  deferred_at: 2026-10-03
