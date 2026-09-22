---
phase: 05-admin-digest-publish
reviewed: 2026-09-21T19:20:00Z
depth: standard
files_reviewed: 19
files_reviewed_list:
  - backend/src/backend/application/ports/digest_publisher.py
  - backend/src/backend/application/use_cases/get_admin_shortlist.py
  - backend/src/backend/application/use_cases/preview_digest_email.py
  - backend/src/backend/application/use_cases/send_digest.py
  - backend/src/backend/domain/errors.py
  - backend/src/backend/domain/shortlist.py
  - backend/src/backend/interface/http/routes/admin.py
  - backend/src/backend/tests_support/in_memory.py
  - supabase-integration/src/supabase_integration/digest_publisher.py
  - tests/admin.spec.js
  - tests/unit/test_admin_preview_composition.js
  - tests/unit/test_get_admin_shortlist.py
  - tests/unit/test_http_admin.py
  - tests/unit/test_preview_digest.py
  - tests/unit/test_send_digest.py
  - tests/web-app.spec.js
  - web/src/pages/AdminDigestPage.jsx
  - web/src/services/adminApi.js
  - web/src/services/adminPreviewComposition.js
findings:
  critical: 1
  warning: 3
  info: 2
  total: 6
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-09-21T19:20:00Z
**Depth:** standard
**Files Reviewed:** 19
**Status:** issues_found

## Summary

Reviewed gap-closure work for plans 05-07 / 05-08 / 05-09 (preview composition, issue-block UI, atomic send path). Domain/use-case gates (draft pool, empty pool, already-sent, exact `material_ids` permutation) and admin HTTP mapping look sound. One critical live-path defect: G-05-1 rank rewrite mutates `digest_shortlist_items` outside `claim_and_publish_digest`, breaking the CR-01 all-or-nothing contract on send failure. Additional warnings cover preview/send order drift, post-claim side effects, and duplicate preview materials.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Publication rank rewrite is not transactional with claim+publish

**File:** `supabase-integration/src/supabase_integration/digest_publisher.py:56-93`
**Issue:** When `material_ids` is provided, `_apply_publication_ranks` issues separate PostgREST `UPDATE`s on `digest_shortlist_items` **before** calling `claim_and_publish_digest`. Each `.execute()` commits independently. If the RPC then fails (race → `AlreadySentError`, empty pool → `EmptySendPoolError`, network/`PersistenceError`) or the process dies mid-loop, shortlist ranks are permanently rewritten on an still-unsent (or partially rewritten) batch. That contradicts the port’s CR-01 guarantee (“publish failure can never leave durable side effects without a recoverable retry”) and can scramble triage ranks for the next attempt. Schema today has PK `(batch_id, material_id)` only (no unique on rank), so the “temp swap” does not make the rewrite atomic with the claim either.
**Fix:** Move ordered publication into the RPC (e.g. `p_material_ids bigint[]`) and `INSERT … SELECT` using `array_position` / `unnest WITH ORDINALITY`, with no pre-RPC rank mutation. Until then, at minimum wrap rewrite+claim in a single Postgres function/transaction and roll ranks back on RPC failure:

```python
# Prefer RPC extension (migration) instead of adapter-side UPDATEs:
# claim_and_publish_digest(..., p_material_ids bigint[] DEFAULT NULL)
# INSERT INTO digest_issue_items (issue_id, material_id, position)
# SELECT v_issue_id, x.material_id, x.ord
# FROM unnest(p_material_ids) WITH ORDINALITY AS x(material_id, ord)
# JOIN ... approved∩ready ...
```

## Warnings

### WR-01: Preview unlock ignores block order; send can diverge from previewed composition

**File:** `web/src/pages/AdminDigestPage.jsx:74-79,182-218,335-343`
**Issue:** D-86 unlock uses `approvedFingerprint` (sorted approved∩ready IDs only). After a successful preview, the admin can reorder «Блоки выпуска» (or edit interstitial text / intro) without invalidating `emailPreviewed`. `confirmSend` then posts the **current** `issueBlocks` order via `material_ids`. Publication/mail order can therefore differ from what was shown in «Превью письма», undermining G-05-1’s composition fidelity.
**Fix:** Include ordered material IDs (and optionally a hash of intro + text blocks) in the fingerprint, or reset `emailPreviewed` whenever `issueBlocks` / `contextText` change:

```javascript
function compositionFingerprint(items, blocks, intro) {
  const materials = (blocks ?? [])
    .filter((b) => b.kind === 'material')
    .map((b) => b.material_id)
    .join(',')
  return `${approvedFingerprint(items)}|${materials}|${String(intro ?? '').trim()}`
}
```

### WR-02: Mailer and ping run after durable claim+publish with no compensation

**File:** `backend/src/backend/application/use_cases/send_digest.py:107-142`
**Issue:** `publisher.claim_and_publish` commits claim + issue first; then `mailer.send_digest` and `pings.record` run. Any exception from mailer/pings leaves a sent batch + published issue while the HTTP layer may surface 5xx/`PersistenceError`→503. Retry correctly hits `AlreadySentError`, but stub/audit side effects can be missing and the UI may show failure after a successful publish. Low probability with `StubMailer`, but the ordering is fragile for any future non-stub mailer.
**Fix:** Record audit inside the same DB transaction as claim/publish when possible; treat mail as best-effort after success (catch + log, still return success); or use an outbox row written atomically with the claim.

### WR-03: Preview accepts duplicate material blocks

**File:** `backend/src/backend/application/use_cases/preview_digest_email.py:86-111`
**Issue:** Explicit `blocks` may list the same `material_id` more than once. Each occurrence is appended to `ordered_materials` / body. Send’s `_ordered_pool` correctly rejects non-permutations (`InvalidSendOrderError`), so a client that mirrors preview duplicates into `material_ids` fails at send after a “successful” preview.
**Fix:** Reject duplicates during preview composition:

```python
seen: set[int] = set()
# inside material branch:
if block.material_id in seen:
    raise InvalidPreviewCompositionError(material_id=block.material_id)
seen.add(block.material_id)
```

## Info

### IN-01: Adapter comment overstates unique(rank) constraint

**File:** `supabase-integration/src/supabase_integration/digest_publisher.py:57-59`
**Issue:** Comment says `digest_shortlist_items typically unique(batch_id, rank)`, but `001_initial_schema.sql` defines only `primary key (batch_id, material_id)`. The two-phase temp-rank dance is unnecessary for uniqueness today (and still insufficient for atomicity — see CR-01).
**Fix:** Align the comment with the real schema, or add a real unique constraint only after ranks are owned entirely inside the RPC.

### IN-02: In-memory publisher maps bad `material_ids` to `EmptySendPoolError`

**File:** `backend/src/backend/tests_support/in_memory.py:485-489`
**Issue:** Incomplete/unknown `material_ids` raise `EmptySendPoolError` after claim+release, whereas the use-case raises `InvalidSendOrderError` before calling the publisher. Harmless while `send_digest` always validates first; misleading if tests call the publisher directly.
**Fix:** Raise `InvalidSendOrderError` (or assert invariants) when `material_ids` is not an exact permutation of the pool.

---

_Reviewed: 2026-09-21T19:20:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
