---
phase: 14-draft-ready-justification-honesty
reviewed: 2026-10-03T13:20:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - backend/src/backend/application/use_cases/mark_material_ready.py
  - backend/src/backend/interface/http/routes/admin.py
  - backend/src/backend/domain/material.py
  - backend/src/backend/domain/shortlist.py
  - backend/src/backend/composition/container.py
  - backend/src/backend/tests_support/in_memory.py
  - web/src/services/adminApi.js
  - web/src/services/adminReadyMock.js
  - web/src/pages/AdminDigestPage.jsx
  - web/src/main.jsx
  - backend/src/backend/interface/http/deps.py
findings:
  critical: 1
  warning: 2
  info: 2
  total: 5
status: issues_found
---

# Phase 14: Code Review Report

**Reviewed:** 2026-10-03T13:20:00Z
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

Phase 14’s draft→ready tracer (single + batch), admin authz (`require_admin`), FE promote UX, mocks, and ADUX-06 honesty copy are largely coherent: status-only `with_ready_status`, collection route before `{id}`, employee 403, and exact D-15 empty «Обоснование» are in place. The main defect is a live-path correctness bug: `markReady` treats a post-promote shortlist refetch failure as promote failure, so the UI rolls back to `draft` while the server already saved `ready`, which can strand the send gate on a false draft pool.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Live `markReady` rolls back UI after successful promote when shortlist refetch fails

**File:** `web/src/services/adminApi.js:371-387`
**Also:** `web/src/pages/AdminDigestPage.jsx:342-352`

**Issue:** On the live path, `markReady` POSTs `/admin/materials/{id}/ready`, then **always** calls `fetchShortlist(token)` and returns that result. If the promote POST succeeds but the follow-up GET fails (network blip / 503), `markReady` throws. `promoteReady` treats any thrown error as promote failure and restores the previous items snapshot (`material_status: 'draft'`). The database already has `ready`, so the UI and send-hint logic (`approvedDrafts`) disagree with the server until a full reload succeeds. That can keep «Уберите черновики…» visible and block send incorrectly.

**Fix:** Decouple promote success from shortlist refresh. Prefer returning a success signal from the POST (or applying optimistic ready and treating refetch as best-effort only):

```javascript
// adminApi.js — live markReady
if (!response.ok) {
  throw mapHttpError(response, 'Не удалось сделать ready')
}
try {
  return await fetchShortlist(token)
} catch {
  // Promote persisted; caller keeps optimistic ready / retries fetch.
  return null
}
```

```javascript
// AdminDigestPage.jsx — promoteReady
const dto = await markReady(item.material_id)
if (dto) {
  applyBatch(dto, setItems, setBatchMeta, setDigestRest, setDaysUntilNextBatch)
} else {
  try {
    const refreshed = await fetchShortlist()
    applyBatch(refreshed, setItems, setBatchMeta, setDigestRest, setDaysUntilNextBatch)
  } catch {
    // keep optimistic ready
  }
}
```

Do **not** call `setItems(previous)` unless the POST itself failed.

## Warnings

### WR-01: Batch helper aborts on `PersistenceError`, violating “never abort” and desyncing FE rollback

**File:** `backend/src/backend/application/use_cases/mark_material_ready.py:39-68`
**Also:** `backend/src/backend/interface/http/routes/admin.py:255-261`, `web/src/pages/AdminDigestPage.jsx:371-402`

**Issue:** `mark_materials_ready` only catches `MaterialNotFoundError`. If `repo.save` raises `PersistenceError` mid-batch (live Supabase adapter does), earlier ids remain promoted, the HTTP layer returns **503** with no `results[]`, and `promoteApprovedDrafts` rolls **all** optimistic rows back to draft. Same class of UI/DB desync as CR-01, for partial batch persistence. Docstring/plan must-have say the batch processes ids independently and never aborts on one failure; only not-found is currently handled.

**Fix:** Catch persistence (and unexpected) failures per id into `MarkReadyItemResult(ok=False, error=...)`, always return HTTP 200 with `results[]`. Map only “materials repo missing” to 503 before calling the helper:

```python
for material_id in material_ids:
    try:
        material = mark_material_ready(repo, material_id, now=now)
    except MaterialNotFoundError:
        results.append(MarkReadyItemResult(material_id, False, None, "material_not_found"))
        continue
    except PersistenceError:
        results.append(MarkReadyItemResult(material_id, False, None, "materials_unavailable"))
        continue
    results.append(MarkReadyItemResult(material_id, True, material.status.value, None))
```

### WR-02: Non-empty blank `factors` list still shadows readable flat keys (honesty edge)

**File:** `backend/src/backend/domain/shortlist.py:18-36`

**Issue:** WR-02 already fixed empty `factors: []` fall-through. A **non-empty** `factors` list whose entries are all blank/non-dict (e.g. `{"factors": [{"label": "  "}, "x"], "Релевантность": 0.8, "Свежесть": 0.6}`) still takes the structured branch, yields `labels == []`, and returns `[]` without consulting flat keys — so UI shows D-15 empty copy even when ≥2 readable flat labels exist. Uncommon shape, but same honesty failure mode as the prior empty-list bug.

**Fix:** After filtering structured labels, if none are readable, fall through to the flat-key branch (or treat “no readable structured labels” like empty list):

```python
if isinstance(factors, list) and factors:
    labels = [
        str(f.get("label", "")).strip()
        for f in factors
        if isinstance(f, dict)
    ]
    labels = [x for x in labels if x]
    if not labels:
        labels = [
            str(k).strip()
            for k, _v in score_factors.items()
            if str(k).strip() and k != "factors"
        ]
else:
    ...
```

## Info

### IN-01: `promoteReady` discards successful `markReady` DTO and refetches again

**File:** `web/src/pages/AdminDigestPage.jsx:342-349`
**Also:** `web/src/services/adminApi.js:386-387`

**Issue:** Live `markReady` already returns a shortlist DTO from `fetchShortlist`. `promoteReady` ignores that value and issues a second `fetchShortlist`. Wastes a round-trip and amplifies CR-01’s failure surface.

**Fix:** `const dto = await markReady(...); if (dto) applyBatch(dto, ...)`.

### IN-02: Batch `material_ids` has no upper bound

**File:** `backend/src/backend/interface/http/routes/admin.py:145-148`

**Issue:** `MarkReadyBatchRequest.material_ids` accepts an unbounded list. Admin-only, so not an authz hole, but a single request can trigger N sequential `get`/`save` calls with no cap.

**Fix:** Add a reasonable `Field(max_length=…)` (e.g. shortlist size or small multiple) aligned with product limits.

---

_Reviewed: 2026-10-03T13:20:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
