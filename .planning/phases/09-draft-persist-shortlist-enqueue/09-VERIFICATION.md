---
phase: 09-draft-persist-shortlist-enqueue
verified: 2026-09-27T18:36:11Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-01-PLAN.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-01-SUMMARY.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-02-PLAN.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-02-SUMMARY.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-03-PLAN.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-03-SUMMARY.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-04-PLAN.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-04-SUMMARY.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-CONTEXT.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-COVERAGE.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-DISCUSSION-LOG.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-PATTERNS.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-PLAN-CHECK.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-RESEARCH.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-REVIEW-DISPOSITION.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-REVIEW-FIX.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-REVIEW.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-UAT.md
  - .planning/phases/09-draft-persist-shortlist-enqueue/09-VALIDATION.md
  - data-collection/src/data_collection/__init__.py
  - data-collection/src/data_collection/adapters/deepseek_article.py
  - data-collection/src/data_collection/assemble.py
  - data-collection/src/data_collection/dto/article_draft.py
  - data-collection/src/data_collection/dto/material_draft.py
  - data-collection/src/data_collection/dto/role_kind.py
  - data-collection/src/data_collection/templates/lecture.md
  - data-collection/src/data_collection/templates/podcast.md
  - data-collection/src/data_collection/tests_support/fakes.py
  - ingestion-service/.env.example
  - ingestion-service/pyproject.toml
  - ingestion-service/src/ingestion_service/adapters/persist_errors.py
  - ingestion-service/src/ingestion_service/adapters/supabase_persist.py
  - ingestion-service/src/ingestion_service/application/ports/persist.py
  - ingestion-service/src/ingestion_service/application/use_cases/ingest_until_persist.py
  - ingestion-service/src/ingestion_service/application/use_cases/persist_draft.py
  - ingestion-service/src/ingestion_service/composition/__init__.py
  - ingestion-service/src/ingestion_service/composition/clients.py
  - ingestion-service/src/ingestion_service/composition/settings.py
  - ingestion-service/src/ingestion_service/domain/material_completion.py
  - ingestion-service/src/ingestion_service/mapping/__init__.py
  - ingestion-service/src/ingestion_service/mapping/persist.py
  - ingestion-service/src/ingestion_service/tests_support/__init__.py
  - ingestion-service/src/ingestion_service/tests_support/fakes.py
  - supabase-integration/migrations/007_phase9_persist_draft.sql
  - tests/unit/test_article_draft_internal.py
  - tests/unit/test_article_draft_roles.py
  - tests/unit/test_assemble_material_draft.py
  - tests/unit/test_captions_failure_zero_persist.py
  - tests/unit/test_data_collection_public_api.py
  - tests/unit/test_deepseek_article_adapter.py
  - tests/unit/test_fake_article_generator.py
  - tests/unit/test_ingestion_clients.py
  - tests/unit/test_ingestion_settings.py
  - tests/unit/test_material_completion.py
  - tests/unit/test_material_draft_roles.py
  - tests/unit/test_persist_draft_use_case.py
  - tests/unit/test_persist_error_mapping.py
  - tests/unit/test_persist_idempotency_overflow.py
  - tests/unit/test_persist_port.py
  - tests/unit/test_phase9_migration_007.py
  - tests/unit/test_supabase_draft_persister_contract.py
covered_digest: "v2:sha256:c2a7e5b3ece988764182baefc77e8353d64a64dbab06d63c5a18d6ae717afdb2"
behavior_unverified: 0
overrides_applied: 0
decision_coverage:
  honored: 20
  total: 20
  not_honored: []
  tool_substring:
    honored: 19
    total: 20
    missed: ["D-14a"]
    note: "gsd-tools check.decision-coverage-verify is a substring heuristic. D-14a is honored in live SQL (coalesce p_roles, no CHECK) and 09-CONTEXT.md / 09-REVIEW-DISPOSITION.md (decision A)."
advisory_review:
  source: .planning/phases/09-draft-persist-shortlist-enqueue/09-REVIEW.md
  status: issues_found
  critical: 0
  warning: 3
  info: 3
  note: "WR-02, WR-04, and WR-05 are closed in live code (this stale refresh). WR-01 remains advisory. IN-01 is decision A / by design. IN-02 already closed. IN-03 deferred."
re_verification:
  previous_status: passed
  previous_score: 5/5
  previous_verified: 2026-09-27T16:39:30Z
  stale_reason: "Covered source changed after last verifier run (code-review fixes WR-02 sent-batch fallback removed, WR-05 FOR UPDATE + unique (batch_id, rank), WR-04 composer-based CAP-02) — #4682"
  gaps_closed: []
  gaps_remaining: []
  regressions: []
  hardened_since_prior:
    - "WR-02: conflict path returns only an unsent shortlist row, else P0001; no sent-batch fallback"
    - "WR-04: CAP-02 spy is composed through run_ingest_until_persist (captions → article → assemble → persist)"
    - "WR-05: latest unsent batch selected FOR UPDATE; unique (batch_id, rank) constraint digest_shortlist_items_batch_id_rank_key"
deferred:
  - truth: "Live CLI persist of real captioned videos appears as drafts in /admin/digest"
    addressed_in: "Phase 10"
    evidence: "Phase 10 success criteria: UAT 3–5 real captioned videos; CLI-01/CLI-02/CLI-03"
  - truth: "Typer one-shot prints material_id, slug, batch_id, and rank"
    addressed_in: "Phase 10"
    evidence: "Phase 10 goal / CLI-01"
  - truth: "Idempotent CLI re-run does not create duplicate materials/shortlist rows (operator UX)"
    addressed_in: "Phase 10"
    evidence: "CLI-02 (RPC ON CONFLICT semantics already locked here)"
advisory:
  - finding: "Conflict path returns caller p_slug, not the stored materials.slug (review WR-01)"
    category: other
    reason: "Idempotent re-run with a changed LLM title can print a slug that was never written. Not a ROADMAP SC. No named test is red. CLI-01-adjacent."
    evidence_status: "none provided"
human_verification: []
next_action: "Phase 9 goal achieved. Human UAT 18/18 complete. Proceed to Phase 10 (CLI Composition & UAT)."
next_command: "/gsd-plan-phase 10"
---

# Phase 9: Draft Persist & Shortlist Enqueue Verification Report

**Phase Goal:** A successful draft write lands as `status=draft` with required provenance and appears on an unsent shortlist batch (creating a new batch when the current one is full)
**Verified:** 2026-09-27T18:36:11Z
**Status:** passed
**Re-verification:** Yes — stale fingerprint refresh after code-review fixes WR-02 / WR-04 / WR-05 (prior report `passed` 5/5 at 2026-09-27T16:39:30Z; no `gaps:` to close). Human UAT is complete (18/18).

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ------- | ---------- | -------------- |
| 1 | Successful persist inserts `materials` with `status=draft` only (never `ready`) and required provenance fields `source_url`, `youtube_video_id`, `source_author`, `source_published_at`, `provenance_label` (PERS-01 / ROADMAP SC1) | ✓ VERIFIED | RPC INSERT hard-codes `'draft'` / `'статья'`; `MaterialDraft` requires the five provenance fields; adapter forwards them as `p_*` and omits `status`/`ready` (`test_persist_never_forwards_status_or_ready_to_rpc`); live PostgREST row `phase5-admin-draft` exposes those columns with 007 backfill values |
| 2 | The run enqueues `digest_shortlist_items` on the current unsent batch with `decision=pending` (PERS-02 / ROADMAP SC2) | ✓ VERIFIED | RPC inserts `decision='pending'` and `rank = max(rank)+1` on the latest `sent_at IS NULL` batch; `test_persist_idempotency_overflow.py` + SQL contract |
| 3 | When the current unsent batch already has 5 items, the run creates a new unsent batch and enqueues there (ROADMAP SC3) | ✓ VERIFIED | RPC: `v_item_count >= p_batch_size` → new `digest_shortlist_batches`; Settings default `shortlist_batch_size=5`; named test `test_overflow_creates_new_unsent_batch_at_capacity` ranks 1–5 then new batch rank 1 |
| 4 | Persist/enqueue never attaches to a batch with `sent_at` set (ROADMAP SC4) | ✓ VERIFIED | New-write select is `where b.sent_at is null` + `FOR UPDATE`; conflict path now also requires `b.sent_at is null` and raises P0001 if none (`test_migration_007_conflict_path_does_not_fall_back_to_sent_batch`, `test_rerun_when_only_sent_batch_exists_raises_batch_creation_failed`). Prior advisory WR-02 is closed |
| 5 | CAP-02 deferred proof: captions (or article) failure leaves `persist.calls == []` (Phase 7 D-14 / 09-04) | ✓ VERIFIED | Named tests `test_captions_failure_leaves_persist_calls_empty` and `test_article_failure_leaves_persist_calls_empty` run failing `FakeTranscriptProvider` / `FakeArticleGenerator` **through** `run_ingest_until_persist` and assert `spy.calls == []` (and article is not called when captions fail). Prior advisory WR-04 is closed |

**Score:** 5/5 roadmap + CAP-02 must-haves verified (supporting PLAN truths below all VERIFIED)

### Supporting PLAN Truths

| Area | Truth | Status | Evidence |
| ---- | ----- | ------ | -------- |
| 09-01 roles | `ArticleDraft` / `MaterialDraft` `roles: list[RoleKind]`; unknown filtered; empty/`{}` → `["employee"]`; assembler copies `article.roles` | ✓ VERIFIED | `role_kind.normalize_roles`; `test_article_draft_roles.py`; `test_material_draft_roles.py`; `assemble.py` `roles=article.roles` |
| 09-01 templates | `lecture.md` and `podcast.md` name `employee`, `analyst`, `ds` and ask for a JSON array | ✓ VERIFIED | `## Аудитория` section in both templates |
| 09-01 adapter | DeepSeek `process()` validates then `normalize_roles`; `["ds","employee"]` round-trips | ✓ VERIFIED | `deepseek_article.py` after `model_validate`; adapter role tests |
| 09-01 public API | `data_collection.__all__` is exactly the seven existing names; `RoleKind` / `ArticleDraft` off root | ✓ VERIFIED | `__init__.py`; `NEGATIVE_ROOT_NAMES` |
| 09-02 port | `PersistPort.persist(MaterialDraft) -> PersistResult` with frozen `material_id/slug/batch_id/rank` | ✓ VERIFIED | `application/ports/persist.py`; `test_persist_port.py` |
| 09-02 completion | `generate_slug` = `{slugify(title)[:50]}-{video_id}`; `reading_minutes = max(1, ceil(words/200))`; `persist_draft` overwrites both and always calls the port (no video_id pre-check) | ✓ VERIFIED | `material_completion.py`; `persist_draft.py`; `test_persist_draft_has_no_video_id_precheck_or_environ` |
| 09-02 fake | `FakeDraftPersister` records `calls`, stores one result per `youtube_video_id`, supports scripted failures | ✓ VERIFIED | `tests_support/fakes.py`; port + use-case tests |
| 09-02 mapper | `PERSIST_REASONS` exact five; `stage=persist`, `exit_code=1`; context ⊆ `{video_id,slug,batch_id,reason}`; no secret / raw Postgres / traceback | ✓ VERIFIED | `mapping/persist.py`; planted-secret tests |
| 09-03 migration | 007 is idempotent; provenance columns; unique `youtube_video_id`; atomic `persist_draft_and_enqueue`; `security invoker`; revoke public/anon/authenticated; grant `service_role` | ✓ VERIFIED | Migration file + `test_phase9_migration_007.py` (comment-stripped D-09 DDL + WR-02/WR-05 assertions) |
| 09-03 adapter | `SupabaseDraftPersister` is the only non-composition `supabase` import; single `client.rpc(...).execute()`; SDK errors map to `DraftPersistError` subtypes without leaking secrets | ✓ VERIFIED | Grep: only `supabase_persist.py` + `composition/clients.py`; contract tests |
| 09-03 live apply | Migration 007 applied to the shared VM (RPC, columns, unique index, grants, WR-05 re-apply) | ✓ VERIFIED | PostgREST read: provenance columns present; Phase 5 row matches 007 backfill. Human UAT #2 passed (RPC exists, FOR UPDATE in prosrc, `digest_shortlist_items_batch_id_rank_key` live). MCP `describe_table` / `list_functions` / `list_indexes` need `POSTGRES_URL` (unavailable this pass) |
| 09-04 settings | `Settings.from_env({})` keeps supabase fields `None` and `shortlist_batch_size=5`; invalid `SHORTLIST_BATCH_SIZE` raises `ConfigurationError`; secret fields omitted from `repr`/`str` | ✓ VERIFIED | `test_ingestion_settings.py` including `test_settings_repr_and_str_omit_secret_fields`; `repr=False` on `supabase_secret_key` and `deepseek_api_key` |
| 09-04 factories | Blank url/key raises before `create_client`; factories exported; `.env.example` documents empty secrets + `SHORTLIST_BATCH_SIZE=5` | ✓ VERIFIED | `test_ingestion_clients.py`; `.env.example` |
| 09-04 idempotency | Two `persist_draft` calls with the same `youtube_video_id` return identical ids; one stored row; `persist()` may run twice; no content refresh (`ON CONFLICT DO NOTHING`) | ✓ VERIFIED | Fake + RPC conflict path; overflow suite |
| 09-04 composer | `run_ingest_until_persist` is captions → article → assemble → `persist_draft` | ✓ VERIFIED | `ingest_until_persist.py`; CAP-02 tests pass the spy into the composer |

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | Live CLI persist of real videos (operator one-shot against the live RPC) | Phase 10 | ROADMAP Phase 10 SC / CLI-01…CLI-03 |
| 2 | Typer prints `material_id`, `slug`, `batch_id`, `rank` + staged progress + separate `.env` | Phase 10 | CLI-01, CLI-04, CLI-05 |
| 3 | Idempotent CLI re-run does not create duplicate materials/shortlist rows (operator UX) | Phase 10 | CLI-02 (RPC semantics already locked here) |

### Advisory (New Scope, Unevidenced)

New-scope findings from Step 7 / the post-verify code review with no deterministic red test — reported, not blocking. WR-02, WR-04, and WR-05 from the prior report are **closed in live code** by the commits that stale-d this report.

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | Conflict path returns caller `p_slug` (WR-01) | other | new-scope, no deterministic evidence; CLI-01-adjacent |

Closed since prior verify (no longer advisory): WR-02 sent-batch fallback; WR-04 vacuous CAP-02 spy; WR-05 unlocked overflow.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------- | ------- |
| `data-collection/.../dto/role_kind.py` | `RoleKind` + `VALID_ROLES` + `normalize_roles` | ✓ VERIFIED | Closed set `{employee, analyst, ds}` |
| `data-collection/.../dto/article_draft.py` | `roles` + before-validator | ✓ VERIFIED | Default `["employee"]` |
| `data-collection/.../dto/material_draft.py` | `roles` + `slug=""` + `reading_minutes=1` + provenance | ✓ VERIFIED | Assembler still constructs without slug |
| `data-collection/.../assemble.py` | copies `article.roles` | ✓ VERIFIED | Direct field copy |
| `data-collection/.../templates/lecture.md` | audience-role instruction | ✓ VERIFIED | JSON array of three roles |
| `data-collection/.../templates/podcast.md` | audience-role instruction | ✓ VERIFIED | Same section |
| `data-collection/.../adapters/deepseek_article.py` | post-validate role normalize | ✓ VERIFIED | `draft.roles = normalize_roles(...)` |
| `ingestion-service/.../application/ports/persist.py` | `PersistPort` + `PersistResult` | ✓ VERIFIED | `runtime_checkable` Protocol |
| `ingestion-service/.../application/use_cases/persist_draft.py` | enrich + `port.persist` | ✓ VERIFIED | No supabase / no pre-check |
| `ingestion-service/.../application/use_cases/ingest_until_persist.py` | CAP-02 composer | ✓ VERIFIED | Captions → article → assemble → persist_draft |
| `ingestion-service/.../domain/material_completion.py` | slug + reading minutes | ✓ VERIFIED | `python-slugify` |
| `ingestion-service/.../adapters/persist_errors.py` | `DraftPersistError` subtypes | ✓ VERIFIED | Five concrete types |
| `ingestion-service/.../mapping/persist.py` | `map_persist_error` + `PERSIST_REASONS` | ✓ VERIFIED | Allowlisted context |
| `ingestion-service/.../tests_support/fakes.py` | `FakeDraftPersister` + `BatchTrackingFakePersister` | ✓ VERIFIED | Overflow + sent-batch skip + WR-02 raise |
| `supabase-integration/migrations/007_phase9_persist_draft.sql` | columns + unique + RPC + WR-05 lock/rank | ✓ VERIFIED | Exists, substantive, applied (live backfill + UAT #2) |
| `ingestion-service/.../adapters/supabase_persist.py` | `SupabaseDraftPersister` | ✓ VERIFIED | Single named RPC |
| `ingestion-service/.../composition/settings.py` | supabase + batch size + secret-safe repr | ✓ VERIFIED | `repr=False` on secret fields; positive-int validation |
| `ingestion-service/.../composition/clients.py` | service client + persister factories | ✓ VERIFIED | Blank credentials fail closed |
| `ingestion-service/.env.example` | empty URL/key + batch size 5 | ✓ VERIFIED | No `s3cr3t` / JWT-looking value |

`gsd-tools verify artifacts` on 09-01…09-04: all `valid` (20/20 files).

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | ---- | ------ | -------- |
| `ArticleDraft.roles` | `MaterialDraft.roles` | `assemble_material_draft` | ✓ WIRED | Direct copy; no extra role logic |
| LLM JSON `roles` | `ArticleDraft.roles` | `model_validate` then `normalize_roles` | ✓ WIRED | Unknown filtered; empty → `employee` |
| `persist_draft` | `PersistPort` | `port.persist(enriched)` | ✓ WIRED | Use-case imports only domain + port |
| `DraftPersistError` | `IngestError(stage=persist)` | `map_persist_error` | ✓ WIRED | Locked five reasons |
| `SupabaseDraftPersister` | `public.persist_draft_and_enqueue` | `client.rpc(name, params).execute()` | ✓ WIRED | Single call; batch logic in Postgres |
| Postgres/SDK exception | `IngestError(stage=persist)` | subtype then mapper | ✓ WIRED | Mocked-client contract tests |
| `Settings.from_env` | `SupabaseDraftPersister` | `build_supabase_service_client` → `build_supabase_draft_persister` | ✓ WIRED | Composition owns wiring |
| `CaptionsError` | `PersistPort` | `run_ingest_until_persist` | ✓ WIRED | Composer stops before `persist_draft`; spy receives no call |

`gsd-tools verify key-links` reports `invalid` because PLAN `from:` values are symbols, not file paths (`Source file not found`). Manual code trace above is the wiring evidence.

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `assemble_material_draft` | provenance fields | `ArticleDraft` + `VideoMetadata` + label | Yes | ✓ FLOWING |
| `persist_draft` | `slug` / `reading_minutes` | `generate_slug` / `estimate_reading_minutes` | Yes | ✓ FLOWING |
| `run_ingest_until_persist` | persist argument | captions → article → assemble | Yes (short-circuits on captions/article error) | ✓ FLOWING |
| `SupabaseDraftPersister` | RPC params | `MaterialDraft` fields + `batch_size` | Yes (typed `p_*` dict) | ✓ FLOWING |
| `persist_draft_and_enqueue` | `materials.status` | SQL literal `'draft'` | Yes (hard-coded, not caller-supplied) | ✓ FLOWING |
| `persist_draft_and_enqueue` | shortlist `decision` / `rank` | SQL `'pending'` + `max(rank)+1` under `FOR UPDATE` | Yes | ✓ FLOWING |
| Live VM `materials` | provenance columns | Migration 007 backfill | Yes (PostgREST sample) | ✓ FLOWING |
| Live CLI write of a new draft | new `materials` / shortlist rows | Phase 10 Typer | N/A this phase | ✓ DEFERRED |

No hollow stubs on the persist happy path. The adapter is a thin RPC caller; batch/overflow/idempotency/sent-skip live in Postgres.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Phase 9 targeted unit suite (16 files) | `uv run pytest tests/unit/test_article_draft_roles.py tests/unit/test_material_draft_roles.py tests/unit/test_assemble_material_draft.py tests/unit/test_deepseek_article_adapter.py tests/unit/test_fake_article_generator.py tests/unit/test_data_collection_public_api.py tests/unit/test_persist_port.py tests/unit/test_persist_error_mapping.py tests/unit/test_material_completion.py tests/unit/test_persist_draft_use_case.py tests/unit/test_phase9_migration_007.py tests/unit/test_supabase_draft_persister_contract.py tests/unit/test_ingestion_settings.py tests/unit/test_ingestion_clients.py tests/unit/test_persist_idempotency_overflow.py tests/unit/test_captions_failure_zero_persist.py -q` | **163 passed** (was 160 at prior verify) | ✓ PASS |
| Named overflow test | `test_overflow_creates_new_unsent_batch_at_capacity` | ranks 1–5 then new batch rank 1 | ✓ PASS |
| Named sent-batch skip | `test_batch_sent_skips_latest_sent_batch` | enqueue lands on unsent batch | ✓ PASS |
| Named WR-02 re-run | `test_rerun_when_only_sent_batch_exists_raises_batch_creation_failed` | `DraftPersistBatchError(reason=batch_creation_failed)` | ✓ PASS |
| Named CAP-02 composer | `test_captions_failure_leaves_persist_calls_empty` | `spy.calls == []` via `run_ingest_until_persist` | ✓ PASS |
| Named D-09 DDL | `test_migration_007_youtube_video_id_unique_is_ddl_not_comment` | ALTER/CONSTRAINT required | ✓ PASS |
| Named WR-02 SQL | `test_migration_007_conflict_path_does_not_fall_back_to_sent_batch` | single unsent lookup; P0001 if missing | ✓ PASS |
| Named WR-05 SQL | `test_migration_007_locks_unsent_batch_and_unique_rank` | `FOR UPDATE` + unique `(batch_id, rank)` | ✓ PASS |
| Named secret-repr | `test_settings_repr_and_str_omit_secret_fields` | `s3cr3t-k3y-t-09-13` absent from `repr`/`str` | ✓ PASS |
| Named no-status forward | `test_persist_never_forwards_status_or_ready_to_rpc` | no `status`/`ready` in RPC params | ✓ PASS |
| Live provenance columns | Supabase MCP `query` `materials` select provenance + status | `phase5-admin-draft` / `status=draft` / 007 backfill | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No `scripts/*/tests/probe-*.sh` and no PLAN-declared probes | ? SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| PERS-01 | 09-01, 09-02, 09-03, 09-04 | Successful run inserts `materials` with `status=draft` only and provenance fields | ✓ SATISFIED | RPC hard-codes draft; DTO + adapter + live columns; Nyquist no-status-forward test |
| PERS-02 | 09-01, 09-02, 09-03, 09-04 | Enqueue on current unsent batch (`decision=pending`); overflow creates a new unsent batch | ✓ SATISFIED | RPC + `BatchTrackingFakePersister` overflow/sent/WR-02 tests |
| CAP-02 | 09-04 (deferred from Phase 7) | Captions failure writes zero DB rows | ✓ SATISFIED | Composer proof: failing provider inside `run_ingest_until_persist` → `persist.calls == []` |

**Orphaned requirements:** None. REQUIREMENTS.md maps only PERS-01 and PERS-02 to Phase 9. CLI-01…CLI-05 map to Phase 10. CAP-02 maps to Phase 7 (Complete) with the live persist spy deferred into this phase — claimed by 09-04 and satisfied.

PLAN frontmatter `requirements:` on 09-01 through 09-04 is `{PERS-01, PERS-02}` in every plan. Cross-check against REQUIREMENTS.md: every ID accounted for.

### Decision Coverage (09-CONTEXT.md)

`gsd-tools check decision-coverage-verify`: tool substring **19/20** (missed D-14a). Independent code check: **20/20 honored.** Gate is non-blocking.

| Decision | Status | Evidence |
| -------- | ------ | -------- |
| D-01 Port + adapter live in `ingestion-service` | ✓ Honored | No `supabase-integration` workspace dep for persist |
| D-02 Own `supabase` package + composition client | ✓ Honored | `pyproject.toml` `supabase>=2.0,<3`; factories |
| D-03 `PersistResult` four fields | ✓ Honored | Frozen dataclass |
| D-04 Local `DraftPersistError` → `stage=persist` | ✓ Honored | Mapper + locked reasons |
| D-05 Single persist+enqueue RPC | ✓ Honored | `persist_draft_and_enqueue` |
| D-06 Migration 007 is canonical | ✓ Honored | Tracked SQL file; applied on VM |
| D-07 Slug/minutes in Python | ✓ Honored | `persist_draft` enriches before port |
| D-08 Latest unsent batch; full → new | ✓ Honored | RPC `week_start desc, created_at desc` + overflow |
| D-09 Unique `youtube_video_id` | ✓ Honored | `materials_youtube_video_id_key` + comment-stripped DDL test |
| D-10 Re-run no-op (no refresh, no second shortlist row) | ✓ Honored | `ON CONFLICT DO NOTHING` + existing-item lookup |
| D-11 No Python video_id pre-check | ✓ Honored | AST test on `persist_draft.py` |
| D-12 Slug `{slugify(title)[:50]}-{video_id}` | ✓ Honored | `kak-ispolzovat-pgvector-dQw4w9WgXcQ` |
| D-13 `reading_minutes` ceil(words/200) min 1 | ✓ Honored | 100→1, 400→2 |
| D-14 `roles` on ArticleDraft/MaterialDraft | ✓ Honored | RoleKind + templates + adapter |
| D-14a RoleKind closed only in Python; RPC has no CHECK | ✓ Honored | `coalesce(p_roles, '{}')` + comment; REVIEW-DISPOSITION skipped / decision A. Tool substring miss |
| D-15 `format='статья'`, `status='draft'`, `source_id=null` | ✓ Honored | RPC INSERT literals |
| D-16 New batch `week_start = date_trunc('week', current_date)` | ✓ Honored | RPC insert |
| D-17 Rank = `max(rank)+1` | ✓ Honored | RPC + fake |
| D-18 Rejected items count toward capacity | ✓ Honored | `test_rejected_item_counts_toward_batch_capacity` |
| D-19 `SHORTLIST_BATCH_SIZE` default 5 | ✓ Honored | Settings + env example |

### Prohibitions

| Prohibition | Tier | Status | Evidence |
| ----------- | ---- | ------ | -------- |
| MUST NOT export `RoleKind` / `ArticleDraft` from package root | test | ✓ Held | `NEGATIVE_ROOT_NAMES` |
| MUST NOT allow invalid/empty roles to reach persist without `["employee"]` fallback | test | ✓ Held | Validators + adapter tests |
| MUST NOT persist `status=ready` or any status other than `draft` | test | ✓ Held | RPC literal `'draft'`; adapter never forwards `status` |
| MUST NOT enqueue on a batch with `sent_at` set | test | ✓ Held | `sent_at IS NULL` on new-write **and** conflict path; batch_sent + WR-02 raise tests |
| MUST NOT expose `SUPABASE_SECRET_KEY`, raw Postgres, or stack traces in `IngestError` context | test | ✓ Held | Planted-secret mapping + adapter tests + Settings `repr=False` |
| MUST NOT refresh/overwrite existing material content on re-run | test | ✓ Held | `ON CONFLICT DO NOTHING`; fake stores first result |

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `test_article_draft_roles.py` / `test_material_draft_roles.py` | PERS-01 | yes | 0 | no | value | PASS |
| `test_phase9_migration_007.py` | PERS-01 / D-09 / WR-02 / WR-05 | yes | 0 | no | value (comment-stripped DDL + lock/rank) | PASS |
| `test_supabase_draft_persister_contract.py` | PERS-01 | yes | 0 | no | value (provenance + no status) | PASS |
| `test_persist_idempotency_overflow.py` | PERS-02 | yes | 0 | no | behavioral | PASS |
| `test_captions_failure_zero_persist.py` | CAP-02 | yes | 0 | no | behavioral (composer) | PASS |
| `test_ingestion_settings.py` | PERS-01 / T-09-13 | yes | 0 | no | value (repr omit) | PASS |

**Disabled tests on requirements:** 0
**Circular patterns detected:** 0
**Insufficient assertions:** 0 (prior CAP-02 vacuous-spy WARNING is closed by `run_ingest_until_persist`)

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `supabase-integration/migrations/007_phase9_persist_draft.sql` | 164–168 | Returns `p_slug` not stored slug | 📋 Advisory | CLI-01-adjacent; see WR-01 |

No `TBD` / `FIXME` / `XXX` in phase-modified production files. Adapters do not read `os.environ` (`Settings.from_env` in composition is the allowed seam). `supabase` imports are only in `supabase_persist.py` and `composition/clients.py`.

### Human Verification Required

N/A — Infrastructure/foundation phase with no user-facing elements.
All acceptance criteria are verifiable programmatically. Live CLI persist of real videos is Phase 10.

Human UAT already completed this phase: **18/18 passed**, including cold start and live VM apply of migration 007 (RPC, provenance columns, unique `youtube_video_id`, service_role grant, FOR UPDATE, `digest_shortlist_items_batch_id_rank_key`). See `09-UAT.md`.

### Gaps Summary

No gaps found against the phase goal / PERS-01 / PERS-02 / ROADMAP success criteria / CAP-02 deferred composer proof.

Stale-refresh deltas vs 2026-09-27T16:39:30Z:
- Phase 9 suite grew **160 → 163** passing tests (WR-02 SQL + WR-05 SQL + WR-02 fake re-run).
- `covered_digest` regenerated: `v2:sha256:c2a7e5b3ece988764182baefc77e8353d64a64dbab06d63c5a18d6ae717afdb2`.
- Review WR-02, WR-04, and WR-05 are closed in live code; WR-01 stays advisory.
- New artifact `ingest_until_persist.py` wires the CAP-02 spy through a real composer.
- Human UAT 18/18 recorded in `09-UAT.md`.

---

## Verification Metadata

**Verification approach:** Goal-backward (ROADMAP SCs + PLAN must_haves from 09-01…09-04 + CAP-02 deferred proof). SUMMARY.md claims were not treated as evidence.
**Must-haves source:** `.planning/ROADMAP.md` Phase 9 Success Criteria + four PLAN frontmatters (reused from prior report; no `gaps:` to re-scope)
**Automated checks:** 163 phase-9 tests passed; 10 named behavioral tests passed
**Live checks:** PostgREST sample of `materials` provenance columns + 007 backfill values; UAT #2 for WR-05 live apply
**Human checks required:** 0 (UAT complete)
**Advisory review:** 09-REVIEW.md present (0 critical; 3 of 3 remaining warnings closed in code; WR-01 leftover from earlier wave stays advisory)

---
_Verified: 2026-09-27T18:36:11Z_
_Verifier: Claude (gsd-verifier)_
