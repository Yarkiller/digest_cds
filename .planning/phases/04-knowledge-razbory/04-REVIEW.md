---
phase: 04-knowledge-razbory
reviewed: 2026-09-21T12:31:38Z
depth: standard
files_reviewed: 49
files_reviewed_list:
  - backend/src/backend/application/ports/knowledge_chunk_repository.py
  - backend/src/backend/application/ports/notebook_storage.py
  - backend/src/backend/application/ports/query_embedder.py
  - backend/src/backend/application/ports/razbor_repository.py
  - backend/src/backend/application/use_cases/download_razbor_notebook.py
  - backend/src/backend/application/use_cases/get_razbor.py
  - backend/src/backend/application/use_cases/list_razbors.py
  - backend/src/backend/application/use_cases/search_knowledge.py
  - backend/src/backend/composition/container.py
  - backend/src/backend/composition/live.py
  - backend/src/backend/composition/settings.py
  - backend/src/backend/domain/errors.py
  - backend/src/backend/domain/razbor.py
  - backend/src/backend/infrastructure/local_notebook_storage.py
  - backend/src/backend/interface/http/app.py
  - backend/src/backend/interface/http/routes/knowledge.py
  - backend/src/backend/interface/http/routes/razbory.py
  - backend/src/backend/tests_support/in_memory.py
  - playwright.config.js
  - supabase-integration/migrations/004_phase4_knowledge_razbory.sql
  - supabase-integration/src/supabase_integration/__init__.py
  - supabase-integration/src/supabase_integration/knowledge_chunk_repository.py
  - supabase-integration/src/supabase_integration/razbor_repository.py
  - tests/knowledge.spec.js
  - tests/razbory.spec.js
  - tests/unit/test_http_knowledge_search.py
  - tests/unit/test_http_razbory.py
  - tests/unit/test_knowledge_api.js
  - tests/unit/test_live_container_wiring.py
  - tests/unit/test_markdown_toc.js
  - tests/unit/test_razbor_notebook_ui_copy.js
  - tests/unit/test_razbor_use_cases.py
  - tests/unit/test_razbory_api.js
  - tests/unit/test_search_knowledge.py
  - tests/unit/test_supabase_knowledge_chunk_repository_contract.py
  - tests/unit/test_supabase_razbor_repository_contract.py
  - tests/web-app.spec.js
  - web/src/App.jsx
  - web/src/components/AppShell.jsx
  - web/src/components/ChronologyItem.jsx
  - web/src/components/MaterialListRow.jsx
  - web/src/data/mock.js
  - web/src/pages/KnowledgePage.jsx
  - web/src/pages/RazborPage.jsx
  - web/src/pages/RazboryListPage.jsx
  - web/src/services/knowledgeApi.js
  - web/src/services/razboryApi.js
  - web/src/utils/filters.js
  - web/src/utils/markdownToc.js
findings:
  critical: 0
  warning: 5
  info: 3
  total: 8
status: issues
---

# Phase 04: Code Review Report

**Reviewed:** 2026-09-21T12:31:38Z
**Depth:** standard
**Files Reviewed:** 49
**Status:** issues

## Summary

Phase 4 knowledge search + razbory stack was reviewed against Ports & Adapters and TDD (commit history shows red→green). JWT gates, score omission, hybrid RPC privilege (`service_role` only), notebook path containment, and announcement body stripping look sound. No Critical/BLOCKER security or crash defects proved. Five Warnings remain: incorrect tag-label mapping on knowledge hits, live `NOTEBOOK_ROOT` defaulting to CWD, notebook download not status-/extension-gated, mock↔live DTO drift, and mock `content_kind` heuristic drift.

Architecture: use-cases stay free of Supabase/HTTP; adapters map SDK errors to `PersistenceError`; wiring stays in `composition/`. Frontend calls only `knowledgeApi` / `razboryApi`.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: Knowledge hit tags emit slug, not display label

**File:** `backend/src/backend/interface/http/routes/knowledge.py:55`
**Issue:** `_to_item` unpacks `material.tags` as `(label, _slug)`, but `SupabaseMaterialRepository` stores `(tag_slug, tag_label)`. Phase 2 seed has distinct pairs (`rag`/`RAG`, `audit`/`аудит`). Live knowledge hits will show slugs (and miss Cyrillic labels). Unit fixtures use identical slug/label (`pgvector`/`pgvector`), so tests do not catch this. Same unpack pattern exists on materials reader (pre-Phase-4); Phase 4 copied it into knowledge.
**Fix:**
```python
tags = [label for _slug, label in material.tags] if material is not None else []
```
Add a unit assertion where slug ≠ label. Prefer documenting the tuple order on `Material.tags` as `(slug, label)`.

### WR-02: Live notebook root defaults to process CWD

**File:** `backend/src/backend/composition/live.py:53`
**Issue:** `LocalNotebookStorage(settings.notebook_root or ".")` resolves relative `notebook_path` under the API process CWD when `NOTEBOOK_ROOT` is unset. Path containment still blocks `..`, but any relative path present under CWD (and writable into `razbors.notebook_path` via admin/SQL) becomes downloadable. Fail-open vs runbook expectation that `NOTEBOOK_ROOT` is required for live proof.
**Fix:**
```python
if not settings.notebook_root:
    raise ValueError("live container requires NOTEBOOK_ROOT for notebook FileResponse")
notebook_storage=LocalNotebookStorage(settings.notebook_root),
```

### WR-03: Notebook download ignores razbor status and file extension

**File:** `backend/src/backend/application/use_cases/download_razbor_notebook.py:18-23`
**Issue:** Download only checks existence of `notebook_path` then `NotebookStorage.resolve`. An `announcement` row with a path (or a non-`.ipynb` relative file under the root) is still served. UI hides the strip for announcements, but `GET /razbory/{id}/notebook` does not. Defense-in-depth gap if `notebook_path` is ever mis-seeded.
**Fix:**
```python
if razbor.status != RazborStatus.PUBLISHED:
    raise NotebookNotAvailableError(razbor_id=razbor_id)
# in LocalNotebookStorage.resolve, after containment:
if candidate.suffix.lower() != ".ipynb":
    raise NotebookPathInvalidError(raw)
```

### WR-04: Mock vs live `notebook_available` for announcements

**File:** `web/src/services/razboryApi.js:114`
**Issue:** Mock forces `notebook_available: !isAnnouncement && Boolean(row.notebook_path)`. Backend `_to_detail` uses `bool(detail.notebook_path)` for all statuses (`razbory.py:185`), and `get_razbor` keeps `notebook_path` on announcements. Honesty e2e under mocks never sees announcement+notebook; live API can disagree.
**Fix:** Align mock with backend **or** clear `notebook_path` / force `notebook_available=False` in `get_razbor` for `ANNOUNCEMENT` (preferred product rule for D-68).

### WR-05: Mock `content_kind` heuristic weaker than backend

**File:** `web/src/services/razboryApi.js:104-107`
**Issue:** Mock uses `/^##\s+(Качество|Оценка качества)\s*$/m` plus `/\|[^|\n]*\d/`. Backend `detect_content_kind` (`get_razbor.py:35-51`) requires a real markdown table (≥2 rows), skips separator rows, and scans numeric cells. Edge markdown can be `quality` in mocks and `overview` live (or the reverse), breaking RAZB-04 honesty when switching off mocks.
**Fix:** Share one pure helper (or mirror the backend rules exactly in `mockRazborDetail`) and add a parity unit test on the same fixture bodies used by `test_razbor_use_cases`.

## Info

### IN-01: Double-newline pollution in HTTP/composition modules

**File:** `backend/src/backend/interface/http/routes/razbory.py:1-400`
**Issue:** Entire `razbory.py` (and similarly `container.py` sections) was rewritten with blank lines between every statement (noted in `fix(04-07): normalize RazborPage newlines` but route file still polluted). Hurts review/diff noise; not a runtime bug.
**Fix:** Reformat with Black/Ruff once; keep behavior unchanged.

### IN-02: Embed runs before query validation

**File:** `backend/src/backend/composition/container.py:143-158`
**Issue:** `AppContainer.search` calls `embedder.embed(query_text)` before `search_knowledge` raises `empty_query` / `query_too_long`. Harmless for `StubQueryEmbedder`; wasteful/confusing once a remote embedder lands.
**Fix:** Validate (or call `search_knowledge` guards) before embed, or have the use-case accept raw text and embed via an injected port after guards.

### IN-03: Knowledge fail-next window flag is sticky

**File:** `web/src/services/knowledgeApi.js:58-64`
**Issue:** `armFailNextKnowledgeSearch` sets both the one-shot module flag and `window.__DIGEST_FAIL_NEXT_KNOWLEDGE__`. `consumeFailNext` clears only the module flag; the window flag stays true (same sticky pattern as `contentApi`, but undocumented here). Phase 4 Playwright honesty specs do not arm this path today; Retry clears via `clearFailNextKnowledgeSearch`.
**Fix:** Document sticky vs one-shot like `contentApi.js`, or clear the window flag on first consume if one-shot is intended.

---

_Reviewed: 2026-09-21T12:31:38Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
