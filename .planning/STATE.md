---
gsd_state_version: "1.0"
milestone: v1.1
milestone_name: YouTube → LLM → Supabase ingestion
current_phase: 11
current_phase_name: "Address tech debt: captions diagnostics and persist error classification"
current_plan: 3
status: executing
stopped_at: Completed 11-02-PLAN.md
last_updated: "2026-10-02T11:07:26.392Z"
last_activity: 2026-10-02
last_activity_desc: Phase 11 execution started
state_head: 08dd9d4a61c1e5141bd4615ef6771ac9b23f6fa2
progress:
  total_phases: 6
  completed_phases: 10
  total_plans: 23
  completed_plans: 21
  percent: 91
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-27)

**Core value:** Trusted weekly prepared-article issue + one honest vote toward the next разбор
**Current focus:** Phase 11 — Address tech debt: captions diagnostics and persist error classification

## Current Position

Phase: 11 (Address tech debt: captions diagnostics and persist error classification) — EXECUTING
Current Plan: 3
Total Plans in Phase: 4
Status: Ready to execute
Last activity: 2026-10-02 — Completed 11-01-PLAN.md

Progress: [█████████░] 91%

## Performance Metrics

**Velocity:**

- Total plans completed: 49 (37 v1 + 14 v1.1)
- Average duration: ~7min (plans 01–05 timed); 06 ≈ 3min; 07-01 = 4min; 07-02 = 5min; 07-03 = 8min
- Total execution time: ~44min + Phase 6 ~9min + Phase 7 ~17min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1–5 (v1 shipped) | 40 | complete | see MILESTONES |
| 6. Ports & DTOs | 3/3 | complete | ~3min |
| 7. Captions Adapter | 3/3 | complete | ~6min |
| 8. DeepSeek Article & Templates | 4/4 | complete | ~52min inline |
| 9. Draft Persist & Shortlist Enqueue | 4/4 | complete | ~7min |
| 10. CLI Composition & UAT | - | - | - |
| 09 | 4 | - | - |
| 10 | 5 | - | - |

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
| 09 | 01 | 5min | 2 | 14 |
| 09 | 02 | 5min | 3 | 15 |
| 09 | 03 | 12min | 4 | 6 |
| 09 | 04 | 7min | 4 | 9 |

**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 09 P01 | 5 min | 2 tasks | 14 files |
| Phase 09 P02 | 5 min | 3 tasks | 15 files |
| Phase 09 P03 | 12min | 4 tasks | 6 files |
| Phase 09 P04 | 7 min | 4 tasks | 9 files |
| Phase 10 P01 | 12min | 3 tasks | 11 files |
| Phase 10 P02 | 20min | 3 tasks | 7 files |
| Phase 10 P03 | 15min | 2 tasks | 2 files |
| Phase 10 P05 | 25min | 2 tasks | 5 files |
| Phase 10 P04 | 48h | 3 tasks | 5 files |
| Phase 11 P01 | 4min | 2 tasks | 3 files |
| Phase 11 P02 | 6min | 2 tasks | 2 files |

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
- [Phase 09]: RoleKind is a first-class list on ArticleDraft and MaterialDraft; unknown/empty falls back to employee.
- [Phase 09]: PersistPort + persist_draft lock slug format `{slugify(title)[:50]}-{video_id}`, locked PERSIST_REASONS, and D-11 no Python video_id pre-check. FakeDraftPersister stores first PersistResult per video_id.
- [Phase 09 / 09-03]: User replied **proceed** on the one-way schema gate. Accepted as one-way: **D-05** (single persist+enqueue RPC), **D-06** (migration 007 is the canonical record), **D-09** (unique constraint on `materials.youtube_video_id`). Undo requires a follow-up migration. Task 1 recorded before any `007_phase9_persist_draft.sql` authoring.
- [Phase 09]: D-05/D-06/D-09 proceed; user pushed 007 via Studio; persist_draft_and_enqueue live; unique youtube_video_id — One-way schema gate accepted; shared VM apply confirmed by human (RPC 1, columns 4, unique index, service_role execute).
- [Phase 09]: Composition owns Supabase service-role wiring; blank url/key raises ConfigurationError before create_client; persist idempotency/overflow proven on the fake port; CAP-02 captions failure leaves persist.calls empty. — Adapters must not read os.environ. D-11 keeps idempotency in the port/RPC, not a Python pre-check. Phase 7 D-14 deferred the persist spy to Phase 9.
- [Phase 10]: build_ingest_deps SimpleNamespace seam for CliRunner monkeypatch
- [Phase 10]: PersistResult.already_saved defaults False until 10-05 live RPC parse
- [Phase 10]: Consistency context allowlist is only transcript_video_id + metadata_video_id (T-10-04)
- [Phase 10]: TemplateLoadError shares ConfigurationError D-08 human branch — no new IngestError stage
- [Phase 10]: Proceed with one-way RPC amend for stored slug + already_saved (D-09, D-12)
- [Phase 10]: Conflict slug via select m.slug into v_slug; insert path keeps p_slug
- [Phase 10]: Migration 008 applied via Studio SQL; human verified RPC already_saved and service_role-only execute
- [Phase 10]: Adapter maps bool(payload already_saved); missing key raises DraftPersistRpcError
- [Phase 10]: CLI-03 closed on the D-14 four-video matrix; D-16 body, provenance, and headings confirmed on /materials/<slug>
- [Phase 10]: Admin preview and email-HTML gaps are Phase 11 follow-ups, not CLI-03 failures, and were not implemented in 10-04
- [Phase 10]: Approval note omitted full watch URLs; 10-UAT.md keeps the operator ellipsized slugs and material ids 9-12
- [Phase 11]: No production edits: Phase 7 catch/mapper already satisfy D-01…D-05; 11-01 added regression tests only
- [Phase 11]: CookieInvalid CliRunner path injected via FakeTranscriptProvider CaptionsError(exception_class=CookieInvalid)
- [Phase 11]: D-09 one-way RPC amend accepted (proceed): migration 009 will return already_saved true on sent-batch-only conflict instead of P0001; consistency with D-08/D-09/D-10; live apply deferred to 11-04
- [Phase 11]: D-09 one-way: migration 009 CREATE OR REPLACE persist_draft_and_enqueue for sent-batch already_saved (user proceed) — Q4/D-08/D-09; undo needs follow-up migration; Studio apply in 11-04
- [Phase 11]: Keep PERSIST_REASONS unchanged (D-07); classification-only fix for 23514 + int HTTP
- [Phase 11]: Int HTTP → rpc_error per D-06 (not network_error)

### Pending Todos

None. Next: `/gsd-verify-work 10`

### Blockers/Concerns

Signup confirmation mail (`g-01-3b-signup-mailer`) remains open from v1 (not this milestone).
gsd-tools ROADMAP atomic rename hit EPERM (file lock); ROADMAP already marked Phase 7 Complete — STATE advanced manually.
Phase 8 `state.planned-phase` rename also hit EPERM; STATE advanced manually to ready to execute.
Phase 9 review ledger closed except IN-03 (deferred, low) and leftover advisory: conflict path still returns caller `p_slug` rather than stored slug (CLI-01-adjacent). `09-SECURITY.md` verified, `threats_open: 0`. Human UAT 18/18 including live VM re-apply of migration 007.

### Roadmap Evolution

- Phase 11 added: Address tech debt: captions diagnostics and persist error classification

## Deferred Items

Carried from v1 close — see prior STATE / MILESTONES. Not in v1.1 scope:
leaderboard, quiz, PIPE-01 YAML UI, live SMTP, signup mail, Whisper/Foundry ASR, ingest HTTP/scheduler.

## Session Continuity

Last session: 2026-10-02T11:07:25.827Z
Stopped at: Completed 11-02-PLAN.md
Resume file: None
Next: `/gsd-verify-work 10`
