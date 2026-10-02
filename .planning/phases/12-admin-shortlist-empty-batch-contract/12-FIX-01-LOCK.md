# FIX-01 Lock — Admin shortlist empty-batch HTTP contract

**Phase:** 12-admin-shortlist-empty-batch-contract  
**Artifact:** `12-FIX-01-LOCK.md` (D-10)  
**Requirement:** FIX-01  
**Authority:** Downstream planners/executors/verifiers MUST read this before changing `GET /admin/shortlist` empty paths, HTTP units, FE mocks, or Playwright empty coverage.

**Proven by (12-01 / D-05):**
- `test_admin_shortlist_no_batches_returns_null_batch_id`
- `test_admin_shortlist_empty_unsent_batch_returns_batch_id`

---

## Shape 1 — No batches (D-04 #1)

When `get_current_batch()` returns no current unsent batch (repository has no open batch):

| Field | Value | Notes |
|-------|-------|-------|
| `batch_id` | `null` | Distinguishes from empty-unsent |
| `items` | `[]` | Never schema/validation 500 |
| `week_label` | `null` | No batch → no week |
| `sent_at` | `null` | Not a sent/rest state |
| `digest_rest` | `false` | Not digest_rest (G-05-2) |
| `days_until_next_batch` | `null` | Empty default |

Plus any other already-declared `AdminShortlistResponse` fields at their empty defaults. Do **not** invent new API fields in this lock.

---

## Shape 2 — Empty unsent batch (D-04 #2)

When a current unsent batch exists (`sent_at IS NULL`) but `items` is empty:

| Field | Value | Notes |
|-------|-------|-------|
| `batch_id` | `<int>` | Present batch id (e.g. `7` in unit seed) |
| `items` | `[]` | Empty list, HTTP 200 |
| `week_label` | `week_start.isoformat()` | Same as non-empty path (D-06); e.g. `"2026-10-06"` |
| `sent_at` | `null` | Unsent |
| `digest_rest` | `false` | Not digest_rest (G-05-2) |
| `days_until_next_batch` | `null` | Empty default |

`batch_id` null-vs-int and `week_label` null-vs-isoformat MUST remain distinct from Shape 1. Do not collapse these into a single empty shape.

---

## Assert rules (D-08)

HTTP / unit proofs MUST assert **required keys + critical values only**:

- Status `200`
- Required keys present: `batch_id`, `items`, `week_label`, `sent_at`, `digest_rest`, `days_until_next_batch`
- Critical values per shape tables above (`items == []`, `batch_id` null-vs-int, `week_label` null-vs-`week_start.isoformat()`, `sent_at is null`, `digest_rest is false`, `days_until_next_batch is null`)

**Forbidden:** brittle full-body JSON equality such as `response.json() == {…}`. Additive *declared* fields must not force rewriting the whole blob.

---

## Response model posture (D-09)

Keep `AdminShortlistResponse` with `extra="forbid"` (`ConfigDict(extra="forbid")`). Undeclared extras fail construction. Additive API fields require explicit model + test + PR — not silent accept.

---

## Proof test names (D-05)

| Shape | pytest node id |
|-------|----------------|
| No batches (D-04 #1) | `tests/unit/test_http_admin.py::test_admin_shortlist_no_batches_returns_null_batch_id` |
| Empty unsent (D-04 #2) | `tests/unit/test_http_admin.py::test_admin_shortlist_empty_unsent_batch_returns_batch_id` |

Surface: in-memory HTTP units only (`InMemoryShortlistRepository`) — D-07.

---

## Not empty — digest_rest (G-05-2)

After-send rest is a **third** distinct shape (`digest_rest=true`, typically null `batch_id` / null `week_label`, with `days_until_next_batch` set). It MUST NOT be confused with genuine empty (Shapes 1–2). Empty proofs assert `digest_rest is false`.

---

## Citations

D-04, D-05, D-08, D-09, D-10; FIX-01. Prior wave: `12-01-SUMMARY.md`.

---

*Phase: 12-admin-shortlist-empty-batch-contract*  
*Lock authored for plan 12-02*
