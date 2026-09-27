---
phase: 09-draft-persist-shortlist-enqueue
reviewed: 2026-09-27T17:15:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - ingestion-service/src/ingestion_service/composition/settings.py
  - tests/unit/test_ingestion_settings.py
  - tests/unit/test_phase9_migration_007.py
  - tests/unit/test_supabase_draft_persister_contract.py
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 09: Code Review Report

**Reviewed:** 2026-09-27T17:15:00Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Incremental re-review of the four files changed since `b704755` (last `09-REVIEW.md` commit). Scope is composition settings plus the three unit tests that were tightened after the prior report. Production code was not modified in this pass.

**Resolved since the last review.** Prior **IN-02** is gone: `Settings.supabase_secret_key` and `Settings.deepseek_api_key` now use `field(..., repr=False)`, and `test_settings_repr_and_str_omit_secret_fields` asserts both values stay out of `repr`/`str` while remaining readable on the instance. Prior **WR-03**’s unique-constraint hole is also closed: `_normalized_executable_sql()` strips `--` comments, and both provenance-column tests assert `ALTER COLUMN ... SET NOT NULL` plus `ADD CONSTRAINT materials_youtube_video_id_key UNIQUE (youtube_video_id)` on executable SQL, not the header comment `-- Target (D-09): youtube_video_id text not null unique`.

**Still open.** The RPC / skip-sent-batch tests still scan the raw file, so several assertions are satisfied by comments next to the real statements. That is a test-reliability defect: flipping `'draft'` → `'ready'`, dropping `SECURITY INVOKER`, or removing the unsent-batch filter can leave those tests green.

**Otherwise sound.** `settings.py` stays in composition (no `supabase`/`httpx`/`fastapi` imports). Integer env parsers reject non-positive and non-integer values via `ConfigurationError`. The persister contract tests assert real RPC parameter behavior (provenance forwarded, `status`/`ready` absent, planted secrets stripped from mapped errors) rather than unused spies.

## Warnings

### WR-01: RPC SQL tests still match comments, not executable statements

**File:** `tests/unit/test_phase9_migration_007.py:57-78`
**Issue:** `_normalized_executable_sql()` is used only for the unique-column tests. `test_migration_007_creates_persist_draft_and_enqueue_rpc` and `test_migration_007_skips_sent_batches_and_is_idempotent_on_video_id` still run `in text.lower()`. In the current migration those phrases live in comments beside (or instead of) the executable form:

- Line 61: `"security invoker"` is in the section header `-- ... (security invoker; service_role only)` **and** in the function. Deleting the `security invoker` clause leaves the test green.
- Lines 62–63: `"status='draft'"` / `"format='статья'"` appear only as trailing comments on `'draft'` / `'статья'`. Changing the literals to `'ready'` / another format while leaving the comments still passes.
- Lines 74–76: `"sent_at is not null" or "sent_at is null"` is tautological after line 74 already requires `sent_at is null`. `"sent_at is not null"` exists only in the comment on migration line 166. `"existing" or "already exists"` is satisfied by `-- Conflict: ... already exists`.

This is the remaining slice of prior WR-03. It does not re-open the unique-constraint assertion.

**Fix:** Drive these tests through `_normalized_executable_sql()` (or `_sql_without_line_comments()`), and assert the executable fragments:

```python
def test_migration_007_creates_persist_draft_and_enqueue_rpc() -> None:
    executable = _normalized_executable_sql()
    assert "create or replace function public.persist_draft_and_enqueue" in executable
    assert "security invoker" in executable
    assert "'draft'" in executable
    assert "'статья'" in executable
    assert "on conflict (youtube_video_id) do nothing" in executable
    assert "sent_at is null" in executable
    assert "p_batch_size" in executable
    assert "get diagnostics" in executable
    assert "status='draft'" not in executable  # comment-only phrase must not count


def test_migration_007_skips_sent_batches_and_is_idempotent_on_video_id() -> None:
    executable = _normalized_executable_sql()
    assert "and b.sent_at is null" in executable
    assert "v_inserted" in executable
    assert "on conflict (youtube_video_id) do nothing" in executable
    assert "digest_shortlist_items" in executable
    assert "decision" in executable and "'pending'" in executable
```

---

_Reviewed: 2026-09-27T17:15:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
