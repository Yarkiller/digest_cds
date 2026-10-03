---
phase: 14-draft-ready-justification-honesty
reviewed: 2026-10-03T18:45:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - backend/src/backend/application/use_cases/mark_material_ready.py
  - backend/src/backend/composition/container.py
  - backend/src/backend/domain/material.py
  - backend/src/backend/domain/shortlist.py
  - backend/src/backend/interface/http/routes/admin.py
  - backend/src/backend/tests_support/in_memory.py
  - supabase-integration/src/supabase_integration/material_repository.py
  - tests/admin.spec.js
  - tests/unit/test_admin_mark_ready.js
  - tests/unit/test_http_admin.py
  - tests/unit/test_mark_material_ready.py
  - tests/unit/test_score_factors.py
  - tests/unit/test_set_shortlist_decision.py
  - tests/unit/test_supabase_material_repository_embed.py
  - web/src/index.css
  - web/src/main.jsx
  - web/src/pages/AdminDigestPage.jsx
  - web/src/services/adminApi.js
  - web/src/services/adminReadyMock.js
  - web/src/services/adminReadyReconcile.js
findings:
  critical: 0
  warning: 3
  info: 5
  total: 8
status: issues_found
---

# Phase 14: Code Review Report

**Reviewed:** 2026-10-03T18:45:00Z
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

Re-review after the three gap closures. The fixes themselves are sound:

- **PGRST201 embed (14-06)** — `material_relations!material_relations_from_material_id_fkey(to_material_id)` matches the Postgres default constraint name produced by `001_initial_schema.sql` (inline `references materials (id)`, column `from_material_id`) and keeps outgoing-relations semantics. No other bare `material_relations(` embed exists in the repo.
- **Batch-CTA removal (14-07)** — the button, `promoteApprovedDrafts` handler, and `markReadyBatch` import are gone; the per-row «Сделать ready» path and the reordered `sendHint` match the Playwright expectations. No dangling references in `AdminDigestPage.jsx`.
- **Pointer cursor (14-08)** — `@layer base { button:not(:disabled) { cursor: pointer } }` is correctly scoped (utilities layer + `disabled:cursor-not-allowed` still win; `disabled:` selectors don't match `:not(:disabled)`). All submit controls in the app render as `<button>`/`ActionButton`, so the rule covers them.

No BLOCKER was found in the changed code. The remaining defects are the phase's own honesty guarantee leaking on non-string factor labels, a residual rollback path on the single-promote response parse, and a regression test that cannot fail on the one string the embed fix depends on. `backend/src/backend/domain/shortlist.py` is included because a listed test (`tests_unit/test_score_factors.py`) targets its `honest_factor_labels` directly.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: `honest_factor_labels` fabricates labels for non-string structured entries

**File:** `backend/src/backend/domain/shortlist.py:23-27` (cross-referenced from `tests/unit/test_score_factors.py`)
**Issue:** The structured branch coerces *any* present `label` to a string, so non-readable values count as readable factors:

```python
labels = [
    str(f.get("label", "")).strip()
    for f in factors
    if isinstance(f, dict)
]
```

Verified by direct execution against the current source:

```text
honest_factor_labels({'factors':[{'label':None},{'label':None}]}) -> ['None', 'None']
honest_factor_labels({'factors':[{'label':1},{'label':2}]})       -> ['1', '2']
```

Both pass the `len(labels) < 2` gate, so the admin UI renders fabricated «обоснование» chips (`factorText` joins them with ` · `). `score_factors` is JSON from the DB and can legitimately contain `null`/numeric labels; `test_score_factors.py` only covers `""`/`"  "`/`"\t"`/`"\n"`, never a non-string. This defeats the documented D-14/D-15 contract ("never fabricated") and is the phase's central honesty mechanism.

**Fix:** Accept only string labels; skip everything else.

```python
labels = [
    f["label"].strip()
    for f in factors
    if isinstance(f, dict) and isinstance(f.get("label"), str)
]
labels = [x for x in labels if x]
```

Add matrix cases asserting `{"factors": [{"label": None}, {"label": None}]} == []` and that `{"label": 1}` is ignored.

### WR-02: Live `markReady` still rolls a persisted promote back on JSON parse failure

**File:** `web/src/services/adminApi.js:390-395` (consumer: `web/src/pages/AdminDigestPage.jsx:332-369`)
**Issue:** The live path treats a 2xx as successful only if the body parses:

```javascript
if (!response.ok) {
  throw mapHttpError(response, 'Не удалось сделать ready')
}
// Promote persisted; MarkReadyResponse is authoritative (G-14-2 — no refetch coupling).
return response.json()
```

If the promote persisted server-side but the 2xx body is empty/unparseable (proxy truncation, an intermediary `204`, a future route change), `markReady` throws. `promoteReady` then runs `setItems(previous)`, rolling the row back to `draft` and re-arming the D-85 draft block — the exact silent-revert class G-14-2 removed, relocated from the refetch boundary to the response-parse boundary. The absolute guarantee claimed in the comment is not met. `response_model=MarkReadyResponse` makes this unlikely, not impossible.

**Fix:** Treat reaching `response.ok` as authoritative and do not let body parsing determine promote success.

```javascript
if (!response.ok) {
  throw mapHttpError(response, 'Не удалось сделать ready')
}
try {
  return await response.json()
} catch {
  // Persisted; body unreadable — synthesize the authoritative result.
  return { material_id: materialId, status: 'ready' }
}
```

### WR-03: The PGRST201 regression test does not lock the FK hint name

**File:** `tests/unit/test_supabase_material_repository_embed.py:147-153`
**Issue:** The fake raises `PGRST201` only for a bare `material_relations(`, and the assertions require a `!` hint plus `(to_material_id)` but never the exact constraint name:

```python
assert "material_relations!" in spec
assert re.search(r"material_relations![^(]+\(to_material_id\)", spec)
assert "material_relations(to_material_id)" not in spec
```

A typo'd hint such as `material_relations!material_relations_from_material_idfkey(to_material_id)` passes this test while production fails with `PGRST200` (unknown relationship) and the original 503 returns. The one literal the fix depends on is the one assertion the test omits — false-green on a just-fixed blocker.

**Fix:** Assert the exact disambiguated literal.

```python
assert (
    "material_relations!material_relations_from_material_id_fkey(to_material_id)" in spec
)
```

## Info

### IN-01: Batch-promote client/harness surface is now dead code

**File:** `web/src/services/adminApi.js:406-436`, `web/src/main.jsx:30,55`, `web/src/services/adminReadyMock.js:119-142`
**Issue:** After 14-07 removed the CTA, nothing in the application calls `markReadyBatch` / `applyMockMarkReadyBatch`. `getMockMarkReadyBatchCalls` is imported into the `window.__DIGEST_ADMIN_HARNESS__` and `mockMarkReadyBatchCalls` is reset/incremented, but no test or spec references the accessor (only the unit test that asserts the export literal exists). This is dead production surface and bundle weight.
**Fix:** Remove the unused exports/harness wiring (adjust `tests/unit/test_admin_mark_ready.js` accordingly) or add a comment documenting the batch client as intentionally retained for a future batch tool.

### IN-02: `_filter_ready_relations` couples per-related lookup failures to the whole read

**File:** `supabase-integration/src/supabase_integration/material_repository.py:151-181`
**Issue:** With the embed now working, every `get()`/`get_by_slug()` issues 1 + N queries. Any failure in a related-material status query is wrapped as `PersistenceError` and fails the primary read, which the admin route maps to 503. A transient hiccup on a secondary relation re-widens the exact 503 blast radius this phase set out to close.
**Fix:** Degrade gracefully (drop the relation on lookup failure) or resolve all target statuses in a single `.in_("id", ids)` query.

### IN-03: `MarkReadyBatchRequest.material_ids` is unbounded

**File:** `backend/src/backend/interface/http/routes/admin.py:146-148`
**Issue:** The request accepts an arbitrarily long `material_ids` list, driving N sequential `get`/`save` round-trips in one admin call. Admin-only, so not an authz hole, but there is no product-aligned cap.
**Fix:** Add `Field(max_length=…)` (e.g. a small multiple of `MAX_SHORTLIST_ITEMS`) so overflow yields 422.

### IN-04: Broad `except Exception` in batch promote masks defects without logging

**File:** `backend/src/backend/application/use_cases/mark_material_ready.py:70-79`
**Issue:** The catch-all maps any exception — including programming errors such as `TypeError` or an adapter bug — to `error="unexpected_error"` and continues, with no log. Reasonable resilience for D-08, but it can silently hide real defects behind a per-id result that reads as expected partial success.
**Fix:** Call `logger.exception(...)` before appending, or narrow the catch and keep a logged generic fallback.

### IN-05: Mock `sendDigest` order validation is weaker than the backend

**File:** `web/src/services/adminApi.js:625-631`
**Issue:** The mock only checks `materialIds.length !== poolIds.size || materialIds.some(id => !poolIds.has(id))`, which accepts duplicates (`[101, 101]` against pool `{101, 102}`) and silently drops the omitted id. The backend `_ordered_pool` rejects the same input via set equality. Not reachable from the UI today (issue blocks are deduped by `syncIssueBlocks`), but mock/backend contract drift can mask a future regression.
**Fix:** Mirror the backend.

```javascript
const uniqueIds = new Set(materialIds)
if (uniqueIds.size !== poolIds.size || materialIds.some((id) => !poolIds.has(id))) {
  throw new AdminApiError('Некорректный порядок материалов.', { code: 'BAD_REQUEST', retryable: false })
}
```

---

_Reviewed: 2026-10-03T18:45:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
