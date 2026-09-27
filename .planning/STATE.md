---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: YouTube → LLM → Supabase ingestion
current_phase: 9
current_phase_name: Draft Persist & Shortlist Enqueue
status: ready_to_plan
stopped_at: Phase 9 planning
last_updated: "2026-09-27T11:45:00.000Z"
last_activity: 2026-09-27
last_activity_desc: Phase 8 verified — UAT passed, security review secured, transitioned to Phase 9
state_head: a5d5e34
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 0
  completed_plans: 0
  percent: 60
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-27)

**Core value:** Trusted weekly prepared-article issue + one honest vote toward the next разбор
**Current focus:** Phase 9 — Draft Persist & Shortlist Enqueue (ready to plan)

## Current Position

Phase: 9 (Draft Persist & Shortlist Enqueue) — READY TO PLAN
Plan: Not started
Status: Phase 8 complete; ready to plan Phase 9
Last activity: 2026-09-27 — Phase 8 verified — UAT passed, security review secured, transitioned to Phase 9

Progress: [████████████░░░░░░░░] 60% (3 of 5 v1.1 phases complete)

## Performance Metrics

**Velocity:**

- Total plans completed: 43 (37 v1 + 6 v1.1)
- Average duration: ~7min (plans 01–05 timed); 06 ≈ 3min; 07-01 = 4min; 07-02 = 5min; 07-03 = 8min
- Total execution time: ~44min + Phase 6 ~9min + Phase 7 ~17min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1–5 (v1 shipped) | 40 | complete | see MILESTONES |
| 6. Ports & DTOs | 3/3 | complete | ~3min |
| 7. Captions Adapter | 3/3 | complete | ~6min |
| 8. DeepSeek Article & Templates | 4/4 | complete | ~52min inline |
| 9. Draft Persist & Shortlist Enqueue | - | - | - |
| 10. CLI Composition & UAT | - | - | - |

### Execution Metrics

| Phase | Plan | Duration | Tasks | Files |
|-------|------|----------|-------|-------|
| 06 | 01 | 4min | 2 | 18 |
| 06 | 02 | 3min | 2 | 7 |
| 06 | 03 | 2min | 2 | 8 |
| 07 | 01 | 4min | 3 | 17 |
| 07 | 02 | 5min | 4 | 9 |
| 07 | 03 | 8min | 4 | 19 |
| 08 | 01 | 15min | 2 | 13 |
| 08 | 02 | 15min | 2 | 6 |
| 08 | 03 | 12min | 2 | 8 |
| 08 | 04 | 10min | 2 | 6 |

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
- CAP-02 unit-only (D-14); live persist spy deferred to Phase 9/10 with ROADMAP note
- oEmbed + VideoMetadataProvider ship with captions (D-21…D-26)
- D-15 FakeTranscriptProvider.failures owned by 07-02; D-26 FakeVideoMetadataProvider by 07-03
- No schema push / migrations this phase; COVERAGE.md OPT-OUTs for Whisper/poToken/playlist

Phase 7 execution (07-01…07-03):

- List-then-pick captions + exact-netloc URL allowlist + IngestError envelope (D-01/D-07/D-11/D-17)
- `ingestion-service` workspace member live
- Full CaptionsError taxonomy (9 subtypes incl. CaptionsBotChallenge) + adapter SDK mapping (CAP-02, D-12, D-19)
- `map_captions_error` locked D-10 reasons + context allowlist redaction (D-13); FakeTranscriptProvider.failures additive (D-15)
- D-14 Phase 9 note: failing TranscriptProvider + spy PersistPort → persist.calls == []
- VideoMetadataProvider + YouTubeOEmbedAdapter + MetadataError/map_metadata_error + FakeVideoMetadataProvider (D-21…D-26)
- Seven-name public barrel; Settings.youtube_proxy_url + clients; runbook live stubs (D-16…D-20)
- Advisory review (07-REVIEW.md): CR-01 message may embed context secrets; WR-01 Cookie* SDK escape; harden before Phase 10 CLI emits to_dict()

Phase 8 execution (08-01…08-04):

- `openai>=3.0,<4` on `data-collection` and `ingestion-service`; `uv.lock` updated
- `DeepSeekArticleGenerator` with injected `AsyncOpenAI`, `response_format=json_object`, thinking disabled, and `ArticleDraft.model_validate`
- `lecture.md` / `podcast.md` with D-16 headings; `load_article_templates` fails at startup via `TemplateLoadError`
- `ArticleError` taxonomy (8 subtypes) maps to `IngestError(stage=llm)` with locked `LLM_REASONS`
- `ArticleBudgetError` → `stage=llm_truncation` with `char_count`/`max_chars` only
- `Settings` DeepSeek fields + `ConfigurationError`; `build_async_deepseek_client` with timeout 120.0, max_retries 0, trust_env False
- `FakeArticleGenerator.failures` keyed by `video_id`
- `ENGLISH_TRANSLATION_SUFFIX` locked in `ingestion_service.provenance`
- Public `data_collection.__all__` remains seven names; runbook documents DeepSeek env names without a live key
- Verification passed (73 Phase 8 unit tests green); one unrelated pre-existing `test_http_admin.py` failure noted

### Pending Todos

None. Next: `/gsd-execute-phase 8` (optional: `/gsd-code-review 7 --fix` for review findings)

### Blockers/Concerns

Signup confirmation mail (`g-01-3b-signup-mailer`) remains open from v1 (not this milestone).
gsd-tools ROADMAP atomic rename hit EPERM (file lock); ROADMAP already marked Phase 7 Complete — STATE advanced manually.
Phase 8 `state.planned-phase` rename also hit EPERM; STATE advanced manually to ready to execute.

## Deferred Items

Carried from v1 close — see prior STATE / MILESTONES. Not in v1.1 scope:
leaderboard, quiz, PIPE-01 YAML UI, live SMTP, signup mail, Whisper/Foundry ASR, ingest HTTP/scheduler.

## Session Continuity

Last session: 2026-09-27T11:45:00.000Z
Stopped at: Phase 8 complete, ready to plan Phase 9
Resume file: None
Next: `/gsd-discuss-phase 9`
