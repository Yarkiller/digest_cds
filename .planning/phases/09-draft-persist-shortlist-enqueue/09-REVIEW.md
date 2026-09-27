---
phase: 09-draft-persist-shortlist-enqueue
reviewed: 2026-09-27T16:20:00Z
depth: standard
files_reviewed: 38
files_reviewed_list:
  - data-collection/src/data_collection/adapters/deepseek_article.py
  - data-collection/src/data_collection/assemble.py
  - data-collection/src/data_collection/dto/article_draft.py
  - data-collection/src/data_collection/dto/material_draft.py
  - data-collection/src/data_collection/dto/role_kind.py
  - data-collection/src/data_collection/templates/lecture.md
  - data-collection/src/data_collection/templates/podcast.md
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
findings:
  critical: 0
  warning: 5
  info: 3
  total: 8
status: issues_found
---

# Phase 09: Code Review Report

**Reviewed:** 2026-09-27T16:20:00Z
**Depth:** standard
**Files Reviewed:** 38
**Status:** issues_found

## Summary

Phase 9 locks RoleKind on drafts, a `PersistPort` / `persist_draft` use-case, DraftPersistError mapping, migration 007 (`persist_draft_and_enqueue`), `SupabaseDraftPersister`, and composition factories for the service-role client. Advisory review only — production code was not changed.

**Security.** No SQL injection: the RPC is parameterized PL/pgSQL with `set search_path = public`. `map_persist_error` and `SupabaseDraftPersister._safe_context` allowlist context and drop planted secrets / raw Postgres text / stack traces (`from None`). `.env.example` has empty `SUPABASE_*` placeholders. Execute is revoked from `public` / `anon` / `authenticated` and granted to `service_role`. RLS from 001 still hides `status='draft'` from `authenticated` (`materials_select_ready` is `status = 'ready'` only); there is no INSERT policy for authenticated users. `build_supabase_service_client` refuses blank url/key before `create_client`.

**Architecture.** Dependencies point inward: `persist_draft` depends only on `PersistPort` and domain helpers; `python-slugify` stays in domain completion; the only `supabase` imports in ingestion-service are `adapters/supabase_persist.py` and `composition/clients.py`. Composition owns wiring; adapters do not read `os.environ`. Error mapping lives at the mapper, not in the use-case. In-memory fakes implement the port without SDK imports.

**TDD.** Role DTO / adapter / assembler contracts are real behavior tests. Persist error redaction and mocked-RPC mapping are solid. The gaps below are where tests assert comments, unused spies, or fake-only overflow while the live RPC diverges on conflict.

## Warnings

### WR-01: Conflict path returns the caller slug, not the stored slug

**File:** `supabase-integration/migrations/007_phase9_persist_draft.sql:158-163`
**Issue:** After `ON CONFLICT (youtube_video_id) DO NOTHING`, the RPC returns `'slug', p_slug`. `persist_draft` always recomputes `generate_slug(title, youtube_video_id)` before calling the port. A re-run whose LLM title changed therefore reports a slug that was never written (`materials.slug` is unique and left untouched). `FakeDraftPersister` / `BatchTrackingFakePersister` return the first stored `PersistResult.slug`, so the in-memory idempotency proofs do not match the live RPC. Phase 10 CLI output (`PersistResult` is the operator contract) can print a 404 admin slug.
**Fix:** After the material lookup, return the row’s stored slug on both the conflict and insert paths:

```sql
select m.id, m.slug
  into v_material_id, v_slug
  from public.materials m
 where m.youtube_video_id = p_youtube_video_id;

-- ... later:
return jsonb_build_object(
  'material_id', v_material_id,
  'slug', v_slug,
  'batch_id', v_batch_id,
  'rank', v_rank
);
```

Add a unit test that calls persist twice with the same `youtube_video_id` and a different title and asserts `PersistResult.slug` equals the first stored slug (RPC contract, not only the fake).

### WR-02: Conflict path can return a sent batch

**File:** `supabase-integration/migrations/007_phase9_persist_draft.sql:143-156`
**Issue:** Plan 09-03 says an existing material returns its existing **unsent** shortlist row and does not create a new item. The first lookup correctly requires `b.sent_at is null`. If that misses, lines 143–151 fall back to **any** shortlist row, including `sent_at IS NOT NULL`. A re-run after publish then returns a sent `batch_id`/`rank` as if enqueue succeeded. That path is untested (`test_batch_sent_skips_latest_sent_batch` only covers a **new** video against a sent latest batch).
**Fix:** Delete the sent-batch fallback. If no unsent shortlist row exists, keep the existing `P0001` raise. Document that a post-publish re-run is `batch_creation_failed` (or add an explicit “already published, not re-enqueued” reason in a later phase) instead of silently returning a sent batch.

### WR-03: Migration 007 SQL tests match a comment, not the DDL

**File:** `tests/unit/test_phase9_migration_007.py:20`
**Issue:** `assert "youtube_video_id text not null unique" in lower` is satisfied by the header comment `-- Target (D-09): youtube_video_id text not null unique` (migration line 4). The real column is added as nullable `text`, then `SET NOT NULL`, then `add constraint materials_youtube_video_id_key unique (youtube_video_id)`. Removing the unique constraint or the `NOT NULL` alter would still leave the test green. `test_migration_007_skips_sent_batches_and_is_idempotent_on_video_id` is similarly a loose substring scan (`"existing" or "already exists" or "v_inserted"`).
**Fix:** Assert the actual statements, and fail if they appear only in comments:

```python
body = "\n".join(
    line for line in text.splitlines() if not line.lstrip().startswith("--")
)
lower = body.lower()
assert "add constraint materials_youtube_video_id_key unique (youtube_video_id)" in lower
assert "alter column youtube_video_id set not null" in lower
assert "on conflict (youtube_video_id) do nothing" in lower
```

### WR-04: CAP-02 test never composes captions/article with persist

**File:** `tests/unit/test_captions_failure_zero_persist.py:45-69`
**Issue:** Both tests construct a `FakeDraftPersister` spy, raise `CaptionsUnavailable` / `ArticleNetworkError` on a **separate** helper that does not receive the spy, then assert `spy.calls == []`. The spy is never passed into a pipeline. The assertion cannot fail. SUMMARY 09-04 treats this as the deferred CAP-02 proof; it does not lock “captions/article failure ⇒ persist not called.”
**Fix:** Extract a small boundary helper used by Phase 10 (e.g. `run_ingest_until_persist(captions, article, persist)`) and test **that** function: script captions or article to fail and assert `persist.calls == []`. Until that composer exists, drop the “proven” claim or mark the test `pytest.mark.xfail` / skip with a Phase 10 pointer.

### WR-05: Unlocked overflow can exceed `p_batch_size` and duplicate `rank`

**File:** `supabase-integration/migrations/007_phase9_persist_draft.sql:175-203`
**Issue:** The RPC counts items, then inserts, with no `FOR UPDATE` on the chosen batch. `digest_shortlist_items` PK is `(batch_id, material_id)` only — there is no `unique (batch_id, rank)`. Two concurrent `persist_draft_and_enqueue` calls on different videos can both see `v_item_count < p_batch_size`, both insert into the same batch (overflow), and both compute the same `max(rank)+1`. Overflow/capacity tests cover only `BatchTrackingFakePersister`, which is single-threaded and cannot catch this.
**Fix:** Lock the target batch (or take an advisory lock on persist) before counting, and add `unique (batch_id, rank)` in a follow-up migration if duplicate ranks must be impossible. At minimum, document that Phase 10 is single-writer so the race is accepted until a second writer exists.

## Info

### IN-01: RPC does not enforce the closed RoleKind set

**File:** `supabase-integration/migrations/007_phase9_persist_draft.sql:112`
**Issue:** `coalesce(p_roles, '{}'::text[])` writes any `text[]`, including `{}` and `'admin'`. Python `normalize_roles` / DTO validators close the set to `employee|analyst|ds` with an employee fallback. A direct `service_role` RPC call (Studio, another client) bypasses that. `materials.roles` has no CHECK (001 default `'{}'`).
**Fix:** In the RPC, replace empty/unknown roles with `'{employee}'` (or reject with `P0001`). Optional: `CHECK (roles <@ ARRAY['employee','analyst','ds'])` once existing rows are clean.

### IN-02: `Settings` repr includes `supabase_secret_key`

**File:** `ingestion-service/src/ingestion_service/composition/settings.py:51-60`
**Issue:** Frozen dataclass has no custom `__repr__`. `test_settings_source_does_not_log_or_print_secret_key` only greps the source for `print` / `logging`. `str(settings)` / debug logging in Phase 10 would leak the service-role key (and `deepseek_api_key`).
**Fix:** Redact secret fields in `__repr__` (same pattern as other credential holders), e.g. `supabase_secret_key='***' if self.supabase_secret_key else None`.

### IN-03: Environ-access scan skips ingestion-service adapters

**File:** `tests/unit/test_ingestion_settings.py:99-108`
**Issue:** `test_adapters_do_not_read_environ` walks only `data-collection/src/data_collection/adapters`. `SupabaseDraftPersister` correctly does not read `os.environ` (composition does), but a future leak in `ingestion_service/adapters/` would not fail this test.
**Fix:** Also scan `ingestion-service/src/ingestion_service/adapters/*.py`.

---

_Reviewed: 2026-09-27T16:20:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
