---
gsd_state_version: "1.0"
milestone: v1.2
milestone_name: Admin UX + diagnostics + PIPE-01 MVP
current_phase: 14
current_phase_name: Draft→ready & justification honesty
status: planning
stopped_at: Phase 12 complete, ready to plan Phase 14
last_updated: "2026-10-03T21:00:08.546Z"
last_activity: 2026-10-04
last_activity_desc: Phase 12 complete, transitioned to Phase 14
state_head: 9875a5c93c0ab60c16516556f92d767b2c014098
progress:
  total_phases: 5
  completed_phases: 4
  total_plans: 19
  completed_plans: 19
  percent: 57
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-02 — v1.2 milestone)

**Core value:** Trusted weekly prepared-article issue + one honest vote toward the next разбор
**Current focus:** Phase 14 — Draft→ready & justification honesty

## Current Position

Phase: 14 — Draft→ready & justification honesty
Plan: Not started
Status: Ready to plan
Last activity: 2026-10-04 — Phase 12 complete, transitioned to Phase 14

Progress: [██████░░░░] 57%

## Performance Metrics

**Velocity:**

- Total plans completed: 11 (40 v1 + 23 v1.1)
- v1.2 plans completed: 0
- Prior milestone velocity: see MILESTONES.md / archived STATE

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1–5 (v1 shipped) | 40/40 | complete | see MILESTONES |
| 6–11 (v1.1 shipped) | 23/23 | complete | see MILESTONES |
| 12. Empty-batch contract | 3/3 | complete | see per-plan |
| 13. Preview honesty | 0/? | not started | - |
| 14. Draft→ready & justification | 0/? | not started | - |
| 15. CLI --debug | 0/? | not started | - |
| 16. PIPE-01 MVP UI | 0/? | not started | - |
| 13 | 8 | - | - |
| 12 | 3 | - | - |
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 12 P01 | 2min | 2 tasks | 1 files |
| Phase 12 P02 | 5min | 2 tasks | 4 files |
| Phase 12-03 P03 | 6min | 2 tasks | 2 files |
| Phase 13 P01 | 7min | 2 tasks | 7 files |
| Phase 13 P02 | 8min | 3 tasks | 8 files |
| Phase 13 P03 | 5min | 2 tasks | 3 files |
| Phase 13 P06 | 12min | 2 tasks | 6 files |
| Phase 13 P04 | 7min | 2 tasks | 3 files |
| Phase 13 P05 | 45min | 3 tasks | 6 files |
| Phase 13 P07 | 11min | 2 tasks | 5 files |
| Phase 13 P08 | 9min | 2 tasks | 3 files |
| Phase 14 P01 | 5min | 2 tasks | 8 files |
| Phase 14 P02 | 4min | 2 tasks | 6 files |
| Phase 14 P03 | 16min | 3 tasks | 7 files |
| Phase 14 P06 | 6min | 1 tasks | 2 files |
| Phase 14 P07 | 5min | 1 tasks | 3 files |
| Phase 14 P08 | 5min | 1 tasks | 2 files |

## Accumulated Context

### Decisions

Full decision log: `.planning/PROJECT.md` (Key Decisions and `<decisions>`).

v1.2 roadmap locks:

- Phases 12–16 only; continuous numbering after v1.1 Phase 11
- PIPE-01 MVP = config + validation + UI; execution → v1.3
- Live SMTP (MAIL-01) and signup confirmation mail (MAIL-02) deferred to v1.3
- ADUX preview cluster (13) before draft→ready / score_factors (14)
- [Phase 12]: D-03: no production edits — empty-unsent already returned D-04 #2 via get_admin_shortlist
- [Phase 12]: Both empty proofs use required-key asserts (D-08); AdminShortlistResponse keeps extra=forbid (D-09)
- [Phase 12]: D-10 lock tables mirror D-04 #1/#2; digest_rest called out as third non-empty shape (G-05-2)
- [Phase 12]: REQUIREMENTS FIX-01 rephrased per RESEARCH Q2: no-batch + empty-unsent under required-key asserts
- [Phase 12]: D-13: no AdminDigestPage chrome — empty-unsent reuses D-80 empty UI
- [Phase 12]: Playwright RED authorized emptyUnsentDto GREEN (RED_EVIDENCE_OK)
- [Phase 13]: Counts computed in get_admin_shortlist from body_markdown; reading_minutes from stored join
- [Phase 13]: Enrich shortlist via get_current_batch join only — no /admin/materials/:id (D-01)
- [Phase 13]: render_email_html blocks as kind maps; site_url defaults until Plan 06; ban assert-only
- [Phase 13]: AdminItemPreview uses MaterialPage markdown stack; no fetch-on-open (D-01/D-04)
- [Phase 13]: Counts always shown (incl. zeros); provenance omitted when empty (D-05/D-06)
- [Phase 13]: Reuse preview _html_content_blocks in send_digest; no second HTML builder
- [Phase 13]: Optional Mailer body_html + StubMailer.last_body_html additive (A4)
- [Phase 13]: Email honesty is sandboxed iframe srcDoc only; no FE HTML assembly or dangerouslySetInnerHTML
- [Phase 13]: Interstitial paragraph hint under both intro and connecting-text (UI-SPEC E3)
- [Phase 13]: D-20 apply-after-sql: ship 010 + runbook section 4g, operator applies via Studio SQL (postgres); do not defer live scrub
- [Phase 13]: D-20 apply-after-sql completed: 010 applied 2026-10-03 Studio SQL (postgres); PostgREST title probe empty; criterion 4 live honesty claimable
- [Phase 13]: Runbook scrub section is §4g (plan text said §4f; §4f already used for admin shortlist/send E2E)
- [Phase 13]: Preview close stays visible because the header row is outside overflow-y-auto, with cursor-pointer on Закрыть
- [Phase 13]: Long-body mock repeats one sentence forty times only inside fetchShortlist useMocks
- [Phase 13]: Email success branch renders subject and email-preview-frame only; the preview.items ul is not mounted
- [Phase 13]: Close-scroll viewport is 1280x400 so overflow comes from the subject plus the iframe after the items list is gone
- [Phase 14]: Triage ready uses with_ready_status — never publish_material/as_ready/index (D-06)
- [Phase 14]: Single ready route is body-less; MarkReadyResponse extra=forbid (D-07/D-10)
- [Phase 14]: In-memory shortlist overlays material_status for send-bridge fidelity
- [Phase 14]: Batch ready uses HTTP 200 partial success results[] (D-08); never 207/FE-loop
- [Phase 14]: D-02 Approve≠ready locked via asserts + AST import guard
- [Phase 14]: Mock DEFAULT_ITEMS seed owned by getMockDefaultItems (material 104 empty factor_labels)
- [Phase 14]: Batch mock call counter on harness for D-08 Playwright proof
- [Phase 14]: Empty Обоснование is exact D-15 sentence; populated join unchanged

### Pending Todos

None. Phase 13 plans 01–08 are complete and ready for verification.

### Blockers/Concerns

Signup confirmation mail (`g-01-3b-signup-mailer`) remains open from v1 (not this milestone).
Nyquist VALIDATION.md drafts for phases 6–8 remain historical debt (not a v1.2 product requirement).

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| deferred_items | 10/deferred-items.md: pre-existing test_admin_shortlist_empty_batch failure → FIX-01 / Phase 12 | in_roadmap | 2026-10-02 | v1.1→v1.2 |
| debug_sessions | (4 items from v1 close — see MILESTONES.md) | acknowledged | 2026-09-22 | v1 |

Carried product deferrals to v1.3+: leaderboard, quiz, live SMTP, signup mail, Whisper/Foundry ASR, ingest HTTP/scheduler, PIPE execution.

## Session Continuity

Last session: 2026-10-03T18:55:08.811Z
Stopped at: Phase 12 complete, ready to plan Phase 14
Resume file: .planning/phases/14-draft-ready-justification-honesty/14-UAT.md
Next: phase verification
