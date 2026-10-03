---
phase: 14-draft-ready-justification-honesty
reviewed: 2026-10-03T17:05:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - backend/src/backend/application/use_cases/mark_material_ready.py
  - backend/src/backend/domain/shortlist.py
  - backend/src/backend/interface/http/routes/admin.py
  - tests/admin.spec.js
  - tests/unit/test_admin_mark_ready.js
  - tests/unit/test_mark_material_ready.py
  - tests/unit/test_score_factors.py
  - web/src/pages/AdminDigestPage.jsx
  - web/src/services/adminApi.js
  - web/src/services/adminReadyReconcile.js
findings:
  critical: 0
  warning: 3
  info: 4
  total: 7
status: issues_found
---

# Phase 14: Code Review Report

**Reviewed:** 2026-10-03T17:05:00Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

This review covers the plan 14-04 (G-14-2) and 14-05 (G-14-2a/2b) gap-closure. The prior review's CR-01/WR-01/WR-02/IN-01 are materially resolved: `markReady` is decoupled from `fetchShortlist` and returns the authoritative `MarkReadyResponse`; `mark_materials_ready` now maps `PersistenceError` per-id and never aborts the batch; `honest_factor_labels` falls through to flat keys when structured labels are blank; and both promote handlers reconcile the post-promote refetch through the pure `preservePromotedReady` helper. The new pure helper is small, side-effect-free, and correctly unit-tested.

The remaining defects are narrower. `honest_factor_labels` still fabricates labels for non-string structured entries (`str(None)` → `"None"`), which weakens the phase's central honesty guarantee. The single-promote path still couples "promote succeeded" to a successful JSON parse of the POST body, so an unparseable 2xx response would re-introduce the same silent-revert class that G-14-2 removed. And the batch reconcile — the same silent-revert class on the collection endpoint — is only asserted through source-text regexes; no behavioral test exercises a stale batch refetch.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: `honest_factor_labels` fabricates labels for non-string structured entries

**File:** `backend/src/backend/domain/shortlist.py:23-27`
**Issue:** The structured branch stringifies whatever `label` value is present:

```python
labels = [
    str(f.get("label", "")).strip()
    for f in factors
    if isinstance(f, dict)
]
labels = [x for x in labels if x]
```

`str(f.get("label", ""))` turns a present-but-non-string value into a "readable" label. Confirmed by direct execution:

```text
f({'factors':[{'label':None},{'label':None}]})  -> ['None', 'None']
f({'factors':[{'label':1},{'label':2}]})        -> ['1', '2']
f({'factors':[{'label':None},{'label':'real'}]}) -> ['None', 'real']
```

`None`/numeric labels are not readable factor labels, yet they are returned and rendered by the admin UI (`factorText` joins them with ` · `). This defeats the documented contract ("never fabricated") and the D-14/D-15 honesty goal for exactly the shape this function exists to sanitize. No test covers a non-string (`None`/int/bool) label — `test_score_factors.py` only covers `""`, `"  "`, `"\t"`, `"\n"`.

**Fix:** Accept only string labels; skip the rest (blank/non-string are "not readable"):

```python
labels = [
    f["label"].strip()
    for f in factors
    if isinstance(f, dict) and isinstance(f.get("label"), str)
]
labels = [x for x in labels if x]
```

Add a matrix case asserting `honest_factor_labels({"factors": [{"label": None}, {"label": None}]}) == []` and `{"label": 1}` is ignored.

### WR-02: Live `markReady` still ties promote success to JSON parsing — residual silent revert

**File:** `web/src/services/adminApi.js:395-396`
**Also:** `web/src/pages/AdminDigestPage.jsx:349-368`

**Issue:** The G-14-2 fix correctly stops calling `fetchShortlist` inside `markReady`, but the live path still treats a successful POST as successful only if `response.json()` parses:

```python
response = await fetch(...)
if (!response.ok) { throw mapHttpError(...) }
return response.json()   // parse failure => throws
```

If the promote persisted server-side but the 2xx body is empty or unparseable (proxy truncation, a 204 from an intermediary, a future route change), `markReady` throws, and `promoteReady`/`promoteApprovedDrafts` run `setItems(previous)`, rolling the row back to `draft` and re-arming the D-85 draft block. That is the exact silent-revert class this phase set out to eliminate, just relocated from the refetch boundary to the response-parse boundary. The backend currently declares `response_model=MarkReadyResponse`, so likelihood is low, but the guarantee is stated as absolute.

**Fix:** Treat the POST reaching `response.ok` as authoritative; don't let body parsing determine promote success:

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

### WR-03: Batch reconcile (the same silent-revert class) is not behaviorally tested

**File:** `tests/admin.spec.js:332-374`; `tests/unit/test_admin_mark_ready.js:124-150`
**Also:** `web/src/pages/AdminDigestPage.jsx:388-421`

**Issue:** The stale-refetch harness (`__DIGEST_ADMIN_STALE_READY__`) is honoured only by the single-material mock (`adminApi.js:368`); `markReadyBatch` always mutates the seed via `applyMockMarkReadyBatch`. Consequently the batch path's `preservePromotedReady(dto.items, [...okIds])` (line 415) is never exercised against a still-draft refetch. The only test that references it is:

```js
assert.match(batchMatch[0], /preservePromotedReady\(/, 'G-14-2: ...')
```

— a source-text match. If the call were wired with the wrong id set (e.g. all ids instead of `okIds`, or `[]`), or the reconcile were applied to the wrong DTO, no behavioral test would fail. This is the batch half of G-14-2 left regression-unlocked.

**Fix:** Extend the stale harness so `markReadyBatch` (mock) also skips persisting when the flag is armed (or add a dedicated `__DIGEST_ADMIN_STALE_READY_BATCH__`), and add a Playwright case that approves ≥1 batch draft, promotes via the batch CTA, and asserts the ok ids stay `готов` after the still-draft refetch. Keep a pure unit test that feeds `preservePromotedReady` the exact `okIds` array the handler builds.

## Info

### IN-01: Source-text assertions couple wiring tests to implementation

**File:** `tests/unit/test_admin_mark_ready.js:94-150`
**Issue:** The `decoupled markReady` and `reconcile refetch via preservePromotedReady` tests read `adminApi.js` / `AdminDigestPage.jsx` and regex-match source (`body.includes('fetchShortlist') === false`, `/preservePromotedReady\(/`). They can pass with a broken runtime wiring and fail on harmless refactors (reordering, comments, helper extraction). The pure `preservePromotedReady` behavior block (lines 153-204) is the trustworthy part; the wiring assertions add little behavioral signal.
**Fix:** Prefer behavioral coverage (render `promoteReady` with a fake `markReady`/`fetchShortlist` and assert post-refetch state) over grepping the source; keep at most one smoke assertion on the export surface.

### IN-02: Footer `locator("ul")` assertion is a weak proxy for "no duplicate titles"

**File:** `tests/admin.spec.js:268`, `tests/admin.spec.js:353`
**Issue:** `await expect(page.getByTestId("admin-send-footer").locator("ul")).toHaveCount(0)` guards against re-introducing a `<ul>` in the footer, but it does not assert the actual G-14-2b intent (approved-draft titles are not re-listed in the footer). A regression that duplicated titles in a `<div>`/`<ol>` would pass.
**Fix:** Assert the footer does not contain any `approvedDrafts` title (e.g. `expect(footer).not.toContainText(draftTitle)`), or assert the footer exposes only the hint + quantified CTA.

### IN-03: `MarkReadyBatchRequest.material_ids` remains unbounded

**File:** `backend/src/backend/interface/http/routes/admin.py:145-148`
**Issue:** Carried over from the prior review (IN-02, unresolved): the batch request accepts an arbitrarily long `material_ids` list, driving N sequential `get`/`save` calls in one admin request. Admin-only, so not an authz hole, but there is still no product-aligned cap.
**Fix:** Add `Field(max_length=…)` (e.g. `MAX_SHORTLIST_ITEMS` or a small multiple) with a 422 on overflow.

### IN-04: Broad `except Exception` in the batch masks unexpected failures

**File:** `backend/src/backend/application/use_cases/mark_material_ready.py:70-79`
**Issue:** The new catch-all maps any exception (including programming errors like `TypeError`, or a bug in a repository adapter) to `error="unexpected_error"` and continues. This is a reasonable resilience default for D-08, but it can silently hide genuine defects behind a per-id "failure" that looks like expected partial-success.
**Fix:** Keep the per-id resilience, but narrow it where possible and/or log the unexpected exception (e.g. `logger.exception(...)`) so masked defects are observable.

---

_Reviewed: 2026-10-03T17:05:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
