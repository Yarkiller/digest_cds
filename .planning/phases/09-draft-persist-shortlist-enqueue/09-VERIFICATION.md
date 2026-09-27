---
phase: 09-draft-persist-shortlist-enqueue
verified: 2026-09-27T16:10:00Z
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
covered_digest: "v2:sha256:b38528bd84bc19686483ba6c37fb170b631731dbaf023ef542fe51ed625fe182"
behavior_unverified: 0
overrides_applied: 0
decision_coverage:
  honored: 19
  total: 19
  not_honored: []
advisory_review:
  source: null
  status: not_run
  critical: 0
  warning: 0
  info: 0
  note: "Code review capability not invoked during inline execution."
coincidental_reliance_items:
  - truth: "Migration 007 adds materials.youtube_video_id as text not null unique"
    reason: fixture-only
    harden: "SQL contract test matches the comment 'youtube_video_id text not null unique'; production DDL is add-nullable, SET NOT NULL, then UNIQUE constraint materials_youtube_video_id_key. Assert those statements (or live pg_constraint) instead of the comment."
human_verification: []
deferred:
  - truth: "Live CLI persist of real captioned videos appears as drafts in /admin/digest"
    addressed_in: "Phase 10"
    evidence: "Phase 10 success criteria: UAT 3–5 real captioned videos; CLI-01/CLI-02/CLI-03"
  - truth: "Typer one-shot prints material_id, slug, batch_id, and rank"
    addressed_in: "Phase 10"
    evidence: "Phase 10 goal / CLI-01"
next_action: "Phase 9 goal achieved. Proceed to Phase 10 (CLI Composition & UAT)."
next_command: "/gsd-plan-phase 10"
---

# Phase 9: Draft Persist & Shortlist Enqueue Verification Report

**Phase Goal:** A successful draft write lands as `status=draft` with required provenance and appears on an unsent shortlist batch (creating a new batch when the current one is full)  
**Verified:** 2026-09-27T16:10:00Z  
**Status:** passed  
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ------- | ---------- | -------------- |
| 1 | Successful persist inserts `materials` with `status=draft` only (never `ready`) and required provenance fields `source_url`, `youtube_video_id`, `source_author`, `source_published_at`, `provenance_label` (PERS-01 / ROADMAP SC1) | ✓ VERIFIED | RPC INSERT hard-codes `'draft'` / `'статья'`; `MaterialDraft` requires the five provenance fields; adapter forwards them as `p_*` params; live VM rows expose those columns (Phase 5 seed backfilled to `https://example.invalid/phase5-admin-draft`) |
| 2 | The run enqueues `digest_shortlist_items` on the current unsent batch with `decision=pending` (PERS-02 / ROADMAP SC2) | ✓ VERIFIED | RPC inserts `decision='pending'` and `rank = max(rank)+1` on the latest `sent_at IS NULL` batch; `test_persist_idempotency_overflow.py` + SQL contract |
| 3 | When the current unsent batch already has 5 items, the run creates a new unsent batch and enqueues there (ROADMAP SC3) | ✓ VERIFIED | RPC: `v_item_count >= p_batch_size` → new `digest_shortlist_batches`; Settings default `shortlist_batch_size=5`; `test_overflow_creates_new_unsent_batch_at_capacity` ranks 1–5 then new batch rank 1 |
| 4 | Persist/enqueue never attaches to a batch with `sent_at` set (ROADMAP SC4) | ✓ VERIFIED | Batch select is `where b.sent_at is null`; `test_batch_sent_skips_latest_sent_batch`; SQL contract asserts the predicate |
| 5 | CAP-02 deferred proof: captions (or article) failure leaves `persist.calls == []` (Phase 7 D-14 / 09-04) | ✓ VERIFIED | `test_captions_failure_zero_persist.py` — failing `FakeTranscriptProvider` / `FakeArticleGenerator` never reaches `FakeDraftPersister` |

**Score:** 5/5 roadmap + CAP-02 must-haves verified (supporting PLAN truths below all VERIFIED)

### Supporting PLAN Truths

| Area | Truth | Status | Evidence |
| ---- | ----- | ------ | -------- |
| 09-01 roles | `ArticleDraft` / `MaterialDraft` `roles: list[RoleKind]`; unknown filtered; empty/`{}` → `["employee"]`; assembler copies `article.roles` | ✓ VERIFIED | `role_kind.normalize_roles`; `test_article_draft_roles.py`; `test_material_draft_roles.py`; `test_assemble_material_draft_copies_article_roles` |
| 09-01 templates | `lecture.md` and `podcast.md` name `employee`, `analyst`, `ds` and ask for a JSON array | ✓ VERIFIED | `## Аудитория` section; template test |
| 09-01 adapter | DeepSeek `process()` validates then `normalize_roles`; `["ds","employee"]` round-trips | ✓ VERIFIED | `deepseek_article.py` after `model_validate`; adapter role tests |
| 09-01 public API | `data_collection.__all__` is exactly the seven existing names; `RoleKind` / `ArticleDraft` off root | ✓ VERIFIED | `__init__.py`; `NEGATIVE_ROOT_NAMES` |
| 09-02 port | `PersistPort.persist(MaterialDraft) -> PersistResult` with frozen `material_id/slug/batch_id/rank` | ✓ VERIFIED | `application/ports/persist.py`; `test_persist_port.py` |
| 09-02 completion | `generate_slug` = `{slugify(title)[:50]}-{video_id}`; `reading_minutes = max(1, ceil(words/200))`; `persist_draft` overwrites both and always calls the port (no video_id pre-check) | ✓ VERIFIED | `material_completion.py`; `persist_draft.py`; completion + use-case tests |
| 09-02 fake | `FakeDraftPersister` records `calls`, stores one result per `youtube_video_id`, supports scripted failures | ✓ VERIFIED | `tests_support/fakes.py`; port + use-case tests |
| 09-02 mapper | `PERSIST_REASONS` exact five; `stage=persist`, `exit_code=1`; context ⊆ `{video_id,slug,batch_id,reason}`; no secret / raw Postgres / traceback | ✓ VERIFIED | `mapping/persist.py`; planted-secret tests |
| 09-03 migration | 007 is idempotent; provenance columns; unique `youtube_video_id`; atomic `persist_draft_and_enqueue`; `security invoker`; revoke public/anon/authenticated; grant `service_role` | ✓ VERIFIED | Migration file + `test_phase9_migration_007.py`; live column/backfill fingerprint |
| 09-03 adapter | `SupabaseDraftPersister` is the only non-composition `supabase` import; single `client.rpc(...).execute()`; SDK errors map to `DraftPersistError` subtypes without leaking secrets | ✓ VERIFIED | Grep: only `supabase_persist.py` + `composition/clients.py`; contract tests |
| 09-03 live apply | Migration 007 applied to the shared VM (RPC, columns, unique index, grants) | ✓ VERIFIED | PostgREST read: provenance columns present; Phase 5 row matches 007 backfill (`phase5-admin-draft` / `phase5-seed`); operator Studio confirmation. MCP `describe_table` / `list_functions` / `raw_sql` need `POSTGRES_URL` (unavailable); opaque `rpc` errors do not distinguish missing vs raising functions |
| 09-04 settings | `Settings.from_env({})` keeps supabase fields `None` and `shortlist_batch_size=5`; invalid `SHORTLIST_BATCH_SIZE` raises `ConfigurationError` | ✓ VERIFIED | `test_ingestion_settings.py` |
| 09-04 factories | Blank url/key raises before `create_client`; factories exported; `.env.example` documents empty secrets + `SHORTLIST_BATCH_SIZE=5` | ✓ VERIFIED | `test_ingestion_clients.py`; `.env.example` |
| 09-04 idempotency | Two `persist_draft` calls with the same `youtube_video_id` return identical ids; one stored row; `persist()` may run twice; no content refresh (`ON CONFLICT DO NOTHING`) | ✓ VERIFIED | Fake + RPC conflict path; overflow suite |

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | Live CLI persist of real videos (operator one-shot against the live RPC) | Phase 10 | ROADMAP Phase 10 SC / CLI-01…CLI-03 |
| 2 | Typer prints `material_id`, `slug`, `batch_id`, `rank` + staged progress + separate `.env` | Phase 10 | CLI-01, CLI-04, CLI-05 |
| 3 | Idempotent CLI re-run does not create duplicate materials/shortlist rows (operator UX) | Phase 10 | CLI-02 (RPC semantics already locked here) |

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
| `ingestion-service/.../domain/material_completion.py` | slug + reading minutes | ✓ VERIFIED | `python-slugify` |
| `ingestion-service/.../adapters/persist_errors.py` | `DraftPersistError` subtypes | ✓ VERIFIED | Five concrete types |
| `ingestion-service/.../mapping/persist.py` | `map_persist_error` + `PERSIST_REASONS` | ✓ VERIFIED | Allowlisted context |
| `ingestion-service/.../tests_support/fakes.py` | `FakeDraftPersister` + `BatchTrackingFakePersister` | ✓ VERIFIED | Overflow + sent-batch skip |
| `supabase-integration/migrations/007_phase9_persist_draft.sql` | columns + unique + RPC | ✓ VERIFIED | Exists, substantive, applied (live backfill) |
| `ingestion-service/.../adapters/supabase_persist.py` | `SupabaseDraftPersister` | ✓ VERIFIED | Single named RPC |
| `ingestion-service/.../composition/settings.py` | supabase + batch size | ✓ VERIFIED | Positive-int validation |
| `ingestion-service/.../composition/clients.py` | service client + persister factories | ✓ VERIFIED | Blank credentials fail closed |
| `ingestion-service/.env.example` | empty URL/key + batch size 5 | ✓ VERIFIED | No `s3cr3t` / JWT-looking value |

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
| `CaptionsError` | `PersistPort` | CAP-02 spy test | ✓ WIRED | Failure path never calls persist |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `assemble_material_draft` | provenance fields | `ArticleDraft` + `VideoMetadata` + label | Yes | ✓ FLOWING |
| `persist_draft` | `slug` / `reading_minutes` | `generate_slug` / `estimate_reading_minutes` | Yes | ✓ FLOWING |
| `SupabaseDraftPersister` | RPC params | `MaterialDraft` fields + `batch_size` | Yes (typed `p_*` dict) | ✓ FLOWING |
| `persist_draft_and_enqueue` | `materials.status` | SQL literal `'draft'` | Yes (hard-coded, not caller-supplied) | ✓ FLOWING |
| `persist_draft_and_enqueue` | shortlist `decision` / `rank` | SQL `'pending'` + `max(rank)+1` | Yes | ✓ FLOWING |
| Live VM `materials` | provenance columns | Migration 007 backfill | Yes (PostgREST sample) | ✓ FLOWING |
| Live CLI write of a new draft | new `materials` / shortlist rows | Phase 10 Typer | N/A this phase | ✓ DEFERRED |

No hollow stubs on the persist happy path. The adapter is a thin RPC caller; batch/overflow/idempotency live in Postgres.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Phase 9 targeted unit suite (16 files) | `uv run pytest tests/unit/test_article_draft_roles.py tests/unit/test_material_draft_roles.py tests/unit/test_assemble_material_draft.py tests/unit/test_deepseek_article_adapter.py tests/unit/test_fake_article_generator.py tests/unit/test_data_collection_public_api.py tests/unit/test_persist_port.py tests/unit/test_persist_error_mapping.py tests/unit/test_material_completion.py tests/unit/test_persist_draft_use_case.py tests/unit/test_phase9_migration_007.py tests/unit/test_supabase_draft_persister_contract.py tests/unit/test_ingestion_settings.py tests/unit/test_ingestion_clients.py tests/unit/test_persist_idempotency_overflow.py tests/unit/test_captions_failure_zero_persist.py -q` | **156 passed** | ✓ PASS |
| Named overflow test | `test_overflow_creates_new_unsent_batch_at_capacity` (included above) | ranks 1–5 then new batch rank 1 | ✓ PASS |
| Named sent-batch skip | `test_batch_sent_skips_latest_sent_batch` | enqueue lands on unsent batch | ✓ PASS |
| Named CAP-02 spy | `test_captions_failure_leaves_persist_calls_empty` | `spy.calls == []` | ✓ PASS |
| Live provenance columns | Supabase MCP `query` `materials` select provenance + status | Columns present; seed backfill matches 007 | ✓ PASS |
| Full unit suite | `uv run pytest` | **576 passed, 1 failed** | ⚠️ ADVISORY |
| Pre-existing failure | `tests/unit/test_http_admin.py::test_admin_shortlist_empty_batch_returns_200_empty_items` | Extra `sent_at` / `week_label` keys | ⚠️ UNRELATED |

The single failing test is the backend admin shortlist empty-batch contract (pre-existing since Phase 8 verification). It is not on the ingestion persist path.

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No `scripts/*/tests/probe-*.sh` and no PLAN-declared probes | ? SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| PERS-01 | 09-01, 09-02, 09-03, 09-04 | Successful run inserts `materials` with `status=draft` only and provenance fields | ✓ SATISFIED | RPC hard-codes draft; DTO + adapter + live columns |
| PERS-02 | 09-01, 09-02, 09-03, 09-04 | Enqueue on current unsent batch (`decision=pending`); overflow creates a new unsent batch | ✓ SATISFIED | RPC + `BatchTrackingFakePersister` overflow/sent tests |
| CAP-02 | 09-04 (deferred from Phase 7) | Captions failure writes zero DB rows | ✓ SATISFIED | Spy proof `persist.calls == []` (orchestrator is Phase 10) |

**Orphaned requirements:** None. REQUIREMENTS.md maps only PERS-01 and PERS-02 to Phase 9. CLI-01…CLI-05 map to Phase 10.

PLAN frontmatter `requirements:` on 09-01 through 09-04 is `{PERS-01, PERS-02}` in every plan. Cross-check against REQUIREMENTS.md: every ID accounted for.

### Decision Coverage (09-CONTEXT.md)

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
| D-09 Unique `youtube_video_id` | ✓ Honored | `materials_youtube_video_id_key` |
| D-10 Re-run no-op (no refresh, no second shortlist row) | ✓ Honored | `ON CONFLICT DO NOTHING` + existing-item lookup |
| D-11 No Python video_id pre-check | ✓ Honored | AST test on `persist_draft.py` |
| D-12 Slug `{slugify(title)[:50]}-{video_id}` | ✓ Honored | `kak-ispolzovat-pgvector-dQw4w9WgXcQ` |
| D-13 `reading_minutes` ceil(words/200) min 1 | ✓ Honored | 100→1, 400→2 |
| D-14 `roles` on ArticleDraft/MaterialDraft | ✓ Honored | RoleKind + templates + adapter |
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
| MUST NOT persist `status=ready` or any status other than `draft` | test | ✓ Held | RPC literal `'draft'`; no caller `status` param |
| MUST NOT enqueue on a batch with `sent_at` set | test | ✓ Held | `sent_at IS NULL` + batch_sent test |
| MUST NOT expose `SUPABASE_SECRET_KEY`, raw Postgres, or stack traces in `IngestError` context | test | ✓ Held | Planted-secret mapping + adapter tests |
| MUST NOT refresh/overwrite existing material content on re-run | test | ✓ Held | `ON CONFLICT DO NOTHING`; fake stores first result |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `tests/unit/test_phase9_migration_007.py` | 20 | Contract string `youtube_video_id text not null unique` is satisfied by a comment, not the ALTER | 📋 Advisory | Unique+NOT NULL are real (staged DDL). Coincidental-reliance only — see frontmatter |
| `tests/unit/test_captions_failure_zero_persist.py` | 45–55 | Spy is never passed to an orchestrator (Phase 10 does not exist yet) | ℹ️ Info | Matches the contracted Phase 7/9 spy shape; CLI wiring is Phase 10 |

No `TBD` / `FIXME` / `XXX` in phase-modified production files. Adapters do not read `os.environ` (`Settings.from_env` in composition is the allowed seam). `supabase` imports are only in `supabase_persist.py` and `composition/clients.py`.

### Human Verification Required

None. Live CLI persist of real videos is Phase 10. Migration 007 apply was a human Studio checkpoint already completed; this pass independently confirmed provenance columns and the 007 backfill fingerprint on the shared VM.

### Gaps Summary

No gaps found against the phase goal / PERS-01 / PERS-02 / ROADMAP success criteria / CAP-02 deferred spy.

Advisory notes:
- One unrelated pre-existing unit failure in `test_http_admin.py` remains (same as Phase 8).
- SQL contract uniqueness assertion leans on a comment; production constraint is `materials_youtube_video_id_key`.
- MCP introspection (`describe_table`, `list_functions`, `raw_sql`) is unavailable without `POSTGRES_URL`; unique-index and grant bits rest on the applied-migration fingerprint plus the operator Studio check.

---

## Verification Metadata

**Verification approach:** Goal-backward (ROADMAP SCs + PLAN must_haves from 09-01…09-04 + CAP-02 deferred proof)  
**Must-haves source:** `.planning/ROADMAP.md` Phase 9 Success Criteria + four PLAN frontmatters  
**Automated checks:** 156 phase-9 tests passed; full suite 576 passed, 1 unrelated failure  
**Live checks:** PostgREST sample of `materials` provenance columns + 007 backfill values  
**Human checks required:** 0  
**Advisory review:** Not run (inline execution)

---
_Verified: 2026-09-27T16:10:00Z_  
_Verifier: Claude (gsd-verifier)_
