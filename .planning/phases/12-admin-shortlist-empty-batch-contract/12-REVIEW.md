---
phase: 12-admin-shortlist-empty-batch-contract
reviewed: 2026-10-02T16:26:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - tests/unit/test_http_admin.py
  - web/src/services/adminApi.js
  - tests/admin.spec.js
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 12: Code Review Report

**Reviewed:** 2026-10-02T16:26:00Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Phase 12 scoped to FIX-01 empty-batch contract proofs: HTTP units (no-batch vs empty-unsent), FE mock harness (`emptyUnsentDto` + `__DIGEST_ADMIN_EMPTY_UNSENT__`), and Playwright empty-unsent UI. Backend production path was intentionally untouched (D-03); only production-adjacent change is the mock branch in `adminApi.js` behind `useMocks()`.

HTTP units correctly lock D-04 #1/#2 with required-key asserts and admin auth. Mock precedence and `resetAdminHarness` clear look sound. Main gap: Playwright EMPTY_UNSENT only asserts the shared D-80 empty UI and never locks the D-04 #2 DTO fields that distinguish empty-unsent from no-batch, so FE mock shape can drift without failing.

## Warnings

### WR-01: EMPTY_UNSENT Playwright never locks D-04 #2 DTO fields

**File:** `tests/admin.spec.js:128-143`
**Issue:** The new EMPTY_UNSENT case mirrors the no-batch EMPTY UI asserts (heading «Кандидатов пока нет», Обновить, no пайплайн/rows/digest_rest) but never checks that the harness actually returns `batch_id: 7` and ISO `week_label: '2026-10-06'`. Per D-13, `weekDek` is gated by `showTriage` (`itemCount > 0`), so those fields are invisible in the DOM. A regression that makes `__DIGEST_ADMIN_EMPTY_UNSENT__` return `emptyDto()` (null `batch_id` / null `week_label`) would still pass this test while breaking FE/HTTP contract parity claimed by FIX-01 / D-12.
**Fix:** After load, probe the mock DTO (or page state) for the distinguishing fields, e.g.:

```js
const dto = await page.evaluate(async () => {
  const { fetchShortlist } = await import('/src/services/adminApi.js');
  return fetchShortlist('test-token');
});
// Or expose a test-only read of last shortlist DTO via harness.
expect(dto.batch_id).toBe(7);
expect(dto.week_label).toBe('2026-10-06');
expect(dto.digest_rest).toBe(false);
expect(dto.items).toEqual([]);
```

If dynamic import is awkward under Vite, add a small harness helper (e.g. `window.__DIGEST_ADMIN_HARNESS__.peekEmptyUnsentDto()`) that returns `emptyUnsentDto()` and assert that from Playwright.

## Info

### IN-01: Duplicated required-key assert blocks in HTTP proofs

**File:** `tests/unit/test_http_admin.py:209-223` and `255-269`
**Issue:** Both FIX-01 proofs repeat the same six-key presence loop plus value asserts. Drift risk is low today but the loop is copy-paste.
**Fix:** Extract a tiny helper, e.g. `_assert_shortlist_required_keys(body)` / `_assert_empty_shape(body, *, batch_id, week_label)`, shared by both tests.

### IN-02: Near-duplicate Playwright empty vs empty-unsent cases

**File:** `tests/admin.spec.js:111-143`
**Issue:** EMPTY and EMPTY_UNSENT share identical UI expectations; only the sticky flag differs. Combined with WR-01, the second case adds little unique signal beyond “flag is wired.”
**Fix:** Keep both cases (mutual exclusivity of flags matters) but factor shared empty-UI expects into a helper and add the DTO asserts from WR-01 only on EMPTY_UNSENT.

---

_Reviewed: 2026-10-02T16:26:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
