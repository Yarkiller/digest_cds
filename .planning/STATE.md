---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: YouTube → LLM → Supabase ingestion
current_phase: 7
current_phase_name: Captions Adapter
status: in_progress
stopped_at: Completed 07-01-PLAN.md
last_updated: "2026-09-26T19:00:39.000Z"
last_activity: 2026-09-26
last_activity_desc: Completed 07-01 captions adapter tracer
state_head: b1eb411
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 3
  completed_plans: 1
  percent: 33
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-24)

**Core value:** Trusted weekly prepared-article issue + one honest vote toward the next разбор
**Current focus:** Phase 7 — Captions Adapter (07-01 complete; 07-02 next)

## Current Position

Phase: 7 of 10 (Captions Adapter) — v1.1 phases 6–10
Plan: 1 of 3 (07-01 complete)
Status: In progress — next `/gsd-execute-phase 7` (plan 02)
Last activity: 2026-09-26 — 07-01 tracer slice shipped

Progress: [███░░░░░░░] 33% (phase plans)

## Performance Metrics

**Velocity:**

- Total plans completed: 40 (37 v1 + 3 v1.1)
- Average duration: ~7min (plans 01–05 timed); 06-01 = 4min; 06-02 = 3min; 06-03 = 2min
- Total execution time: ~44min + 01-06 docs/human follow-up

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1–5 (v1 shipped) | 40 | complete | see MILESTONES |
| 6. Ports & DTOs | 3/3 | complete | ~3min |
| 7. Captions Adapter | 1/3 | in progress | - |
| 8. DeepSeek Article & Templates | - | - | - |
| 9. Draft Persist & Shortlist Enqueue | - | - | - |
| 10. CLI Composition & UAT | - | - | - |

### Execution Metrics

| Phase | Plan | Duration | Tasks | Files |
|-------|------|----------|-------|-------|
| 06 | 01 | 4min | 2 | 18 |
| 06 | 02 | 3min | 2 | 7 |
| 06 | 03 | 2min | 2 | 8 |
| 07 | 01 | 4min | 3 | 17 |

## Accumulated Context

### Decisions

Full decision log: `.planning/PROJECT.md` (Key Decisions and `<decisions>`).

v1.1 locked for roadmap:

- PERS-02: full unsent batch (5 items) → create new unsent batch (not fail-if-full)
- PERS-01: provenance columns required; migration in scope if missing
- LLM-03/04/05 and CLI-04/05 in scope; DeepSeek MVP, captions only

Phase 6 planning locks (see `06-CONTEXT.md` / `06-RESEARCH.md`):

- `require_material_draft` in `assemble.py`; async fakes via `asyncio.run`; strip/non-blank MaterialDraft strings

Phase 6 execution (06-01…06-03):

- Both port fakes shipped: FakeArticleGenerator + FakeTranscriptProvider (DTO-02)
- DTO-01 empty/blank/language/nullable published_at edges locked; no schema migration
- User approved proceed at 06-03 checkpoint — brownfield DTOs deleted (D-01…D-03)
- Public `__all__` is six ingestion names only; fakes/ArticleDraft not exported (D-04, D-06)
- Backend `query_embedder.EMBEDDING_DIM=1024` untouched; DTO-01/DTO-02 Complete

Phase 7 planning (07-01…07-03):

- Tracer-first: URL parse + IngestError + mocked captions happy path (CAP-01)
- CAP-02 unit-only (D-14); live persist spy deferred to Phase 9/10 with ROADMAP note + 07-02 checkpoint:decision
- oEmbed + VideoMetadataProvider ship with captions (D-21…D-26)
- D-15 FakeTranscriptProvider.failures owned by 07-02; D-26 FakeVideoMetadataProvider by 07-03
- No schema push / migrations this phase; COVERAGE.md OPT-OUTs for Whisper/poToken/playlist

Phase 7 execution (07-01):

- List-then-pick captions + exact-netloc URL allowlist + IngestError envelope (D-01/D-07/D-11/D-17)
- `ingestion-service` workspace member live; CAP-01/CAP-02 shared IDs wait for sibling plans before REQUIREMENTS Complete

### Pending Todos

None. Next: execute `07-02-PLAN.md`

### Blockers/Concerns

Signup confirmation mail (`g-01-3b-signup-mailer`) remains open from v1 (not this milestone).
gsd-tools STATE/ROADMAP atomic rename hit EPERM (file lock); updated via direct edit instead.

## Deferred Items

Carried from v1 close — see prior STATE / MILESTONES. Not in v1.1 scope:
leaderboard, quiz, PIPE-01 YAML UI, live SMTP, signup mail, Whisper/Foundry ASR, ingest HTTP/scheduler.

## Session Continuity

Last session: 2026-09-26T19:00:39.000Z
Stopped at: Completed 07-01-PLAN.md
Resume file: None
Next: `.planning/phases/07-captions-adapter/07-02-PLAN.md`
