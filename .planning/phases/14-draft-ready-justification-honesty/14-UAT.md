---
status: diagnosed
phase: 14-draft-ready-justification-honesty
source: [14-VERIFICATION.md]
started: 2026-10-03T14:13:45Z
updated: 2026-10-03T15:58:31Z
---

## Current Test

[testing complete]

## Tests

### 1. Long title + ready CTA layout
expected: Title wraps with break-words; badge and CTA remain clickable without overflow clipping
result: pass

### 2. Sticky footer with many approved drafts
expected: Approved-draft titles wrap/scroll within the sticky footer without covering the batch CTA hit target
result: issue
reported: "Blocker: per-row «Сделать ready» click does nothing — state unchanged (ADUX-05 core, D-85 unblock broken). UX: [draft] + одобрен reads as contradiction; footer duplicates titles + batch CTA label «одобренные черновики» confusing."
severity: blocker

### 3. Factor caption / empty justification wrap
expected: Long captions and the D-15 empty sentence wrap with break-words inside max-w-[12rem] without breaking the shortlist row grid
result: pass

## Summary

total: 3
passed: 2
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-14-2
  truth: "Per-row «Сделать ready» promotes a draft to ready, clears the D-85 send hint, and updates row state (ADUX-05)"
  status: failed
  reason: "User reported: per-row «Сделать ready» click does nothing — state unchanged; ADUX-05 core function, D-85 unblock path broken. Diagnose: Network tab for POST /admin/materials/{id}/ready; backend logs request_id; check mocks vs live."
  severity: blocker
  test: 2
  root_cause: "promoteReady treats the post-POST shortlist refetch as authoritative and applyBatch() overwrites the optimistic ready back to draft whenever the refetched shortlist still reports draft; live path silently reverts (no toast), mock path masks it by mutating seed before cloneBatch()"
  artifacts:
    - path: "web/src/pages/AdminDigestPage.jsx"
      issue: "promoteReady optimistically sets ready then unconditionally applies refetched DTO via applyBatch, clobbering ready back to draft on still-draft refetch"
    - path: "web/src/services/adminApi.js"
      issue: "markReady (live) couples promote success to fetchShortlist and returns the refetch DTO applied unconditionally"
    - path: "web/src/services/adminReadyMock.js"
      issue: "mock mutates in-memory seed before cloneBatch so reconcile always returns ready, masking the silent-revert class"
  missing:
    - "Decouple promote success from refetch — make POST response the source of truth for row ready state"
    - "Treat refetch as best-effort reconciliation, never silently clobber optimistic ready with a still-draft refetch"
    - "Confirm live backend actually runs Phase 14 mark_material_ready route (check POST /admin/materials/{id}/ready status)"
  debug_session: ".planning/debug/per-row-ready-click-noop.md"

- gap_id: G-14-2a
  truth: "Draft badge and approval state read unambiguously (no contradictory [draft] + одобрен pairing)"
  status: failed
  reason: "User reported: [draft] + одобрен reads as contradiction — tooltip or clearer labels needed"
  severity: minor
  test: 2
  root_cause: "Row renders two independent status axes (raw material_status pill + decision caption «одобрен») unlabelled in the same flex container; D-02 keeps them decoupled by design so an approved draft legitimately carries both"
  artifacts:
    - path: "web/src/pages/AdminDigestPage.jsx"
      issue: "badge container renders material_status pill, «Сделать ready» button, and decision caption in one unlabelled flex row (~759-781); decisionCaption maps only decision"
  missing:
    - "Disambiguate the two axes (tooltip/legend or relabel draft pill; e.g. draft → «черновик», «одобрен (в шортлист)»)"
  debug_session: ".planning/debug/draft-approved-contradiction.md"

- gap_id: G-14-2b
  truth: "Sticky send footer does not duplicate approved-draft titles and the batch CTA label is unambiguous"
  status: failed
  reason: "User reported: footer duplicates titles; batch CTA label «одобренные черновики» confusing — collapse list or count-only, rename CTA"
  severity: minor
  test: 2
  root_cause: "Sticky send footer renders an extra <ul> of approvedDrafts titles (a strict subset already rendered in the shortlist list) and the batch CTA label is a bare noun phrase with no count"
  artifacts:
    - path: "web/src/pages/AdminDigestPage.jsx"
      issue: "footer <ul> (~818-823) duplicates approvedDrafts titles; batch CTA label «Сделать ready одобренные черновики» (~832) ambiguous"
  missing:
    - "Collapse footer title list to count-only summary or drop the <ul> entirely"
    - "Rename CTA to quantified action (e.g. «Сделать ready все одобренные черновики (N)»)"
  debug_session: ".planning/debug/footer-duplicates-cta-label.md"
