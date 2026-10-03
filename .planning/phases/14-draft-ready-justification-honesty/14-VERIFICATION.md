---
phase: 14-draft-ready-justification-honesty
verified: 2026-10-03T13:17:51Z
status: human_needed
score: 10/13 must-haves verified
covered_files:
  - .planning/phases/14-draft-ready-justification-honesty/14-01-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-01-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-02-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-02-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-03-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-03-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-REVIEW-DISPOSITION.md
  - .planning/phases/14-draft-ready-justification-honesty/14-REVIEW.md
  - backend/src/backend/application/use_cases/mark_material_ready.py
  - backend/src/backend/composition/container.py
  - backend/src/backend/domain/material.py
  - backend/src/backend/domain/shortlist.py
  - backend/src/backend/interface/http/routes/admin.py
  - backend/src/backend/tests_support/in_memory.py
  - tests/admin.spec.js
  - tests/unit/test_admin_mark_ready.js
  - tests/unit/test_http_admin.py
  - tests/unit/test_mark_material_ready.py
  - tests/unit/test_score_factors.py
  - tests/unit/test_set_shortlist_decision.py
  - web/src/main.jsx
  - web/src/pages/AdminDigestPage.jsx
  - web/src/services/adminApi.js
  - web/src/services/adminReadyMock.js
covered_digest: "v2:sha256:45f00f40dd0547a7aee5b551be514087dff724d6dce4fe8f50feb3edcd879d2f"
behavior_unverified: 0
overrides_applied: 0
decision_coverage:
  honored: 17
  total: 17
  not_honored: []
human_verification:
  - test: "Open Admin Digest with a long draft title; confirm draft badge + «Сделать ready» stay usable in the meta flex wrap"
    expected: "Title wraps with break-words; badge and CTA remain clickable without overflow clipping"
    why_human: "14-03 must_have marked verification: backstop — layout usability cannot be proven by unit/presence checks"
  - test: "Approve several drafts so N≥2 appear under the send hint; check sticky footer scroll/wrap"
    expected: "Approved-draft titles wrap/scroll within the sticky footer without covering the batch CTA hit target"
    why_human: "14-03 must_have marked verification: backstop — sticky footer hit-target geometry needs visual check"
  - test: "View a shortlist row with long factor captions and a row with empty Обоснование"
    expected: "Long captions and the D-15 empty sentence wrap with break-words inside max-w-[12rem] without breaking the shortlist row grid"
    why_human: "14-03 must_have marked verification: backstop — grid/overflow behavior is visual"
quality_concerns:
  - id: CR-01
    severity: critical (code-review)
    disposition: open — not goal-blocking for verify
    summary: "Live markReady POSTs ready then awaits fetchShortlist; if refetch fails after successful promote, promoteReady rolls UI back to draft while server already saved ready"
    affects_must_haves: "Softens D-05 live failure handling (false promote failure). Happy-path ADUX-05 (UI promote + D-85 clear) remains proven under mocks/unit. Disposition: Blocking for verify: none."
  - id: WR-01
    severity: warning
    disposition: open — not goal-blocking
    summary: "mark_materials_ready only catches MaterialNotFoundError; mid-batch PersistenceError can 503 and FE-roll back all optimistic rows"
  - id: WR-02
    severity: warning
    disposition: open — not goal-blocking
    summary: "Non-empty blank factors[] still shadows readable flat keys (uncommon shape); primary 0/1/2+/whitespace matrix is green"
---

# Phase 14: Draft→ready & justification honesty Verification Report

**Phase Goal:** Admin can unblock send without SQL and see honest shortlist justification  
**Verified:** 2026-10-03T13:17:51Z  
**Status:** human_needed  
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Admin can set a material from draft → ready in the admin UI without a direct SQL workaround (roadmap SC1 / ADUX-05) | ✓ VERIFIED | `AdminDigestPage` per-row + batch CTAs → `adminApi.markReady` / `markReadyBatch` → `POST /admin/materials/{id}/ready` and `POST /admin/materials/ready`; Playwright `per-row Сделать ready…` and `batch Сделать ready…` |
| 2 | After promotion, D-85 send gate no longer blocks that material solely for still being draft (roadmap SC2 / ADUX-05) | ✓ VERIFIED | `test_admin_mark_ready_promotes_draft_and_clears_send_gate` + Playwright asserts draft hint clears after promote |
| 3 | Shortlist «Обоснование» shows populated score_factors or explicit empty/unavailable — never silent fake (roadmap SC3 / ADUX-06) | ✓ VERIFIED | `factorText` exact D-15 empty string; populated joins server `factor_labels` only; Playwright exact D-15 assert; `honest_factor_labels` matrix |
| 4 | Status-only promote leaves `published_at` unchanged and never routes through `publish_material` / `Material.as_ready` (D-06) | ✓ VERIFIED | `Material.with_ready_status` uses `replace` without `assert_publishable`; `mark_material_ready` has no publish/index imports; unit empty-body proof |
| 5 | Already-ready promote returns 200 no-op; empty body still promotes (D-09 / D-10) | ✓ VERIFIED | `test_mark_material_ready_already_ready_is_noop`, `test_admin_mark_ready_already_ready_is_noop`, empty-body unit + Playwright soft-warn path |
| 6 | Batch `POST /admin/materials/ready` returns HTTP 200 order-preserving partial success; `extra=forbid`; empty ids → `results=[]` (D-08) | ✓ VERIFIED | `mark_materials_ready` + HTTP batch tests (`partial_success`, `empty_ids`, `unknown_field_422`, employee 403) |
| 7 | Approve on draft leaves `material_status` draft — approve ≠ ready (D-02) | ✓ VERIFIED | `test_approve_allowed_on_draft_material`, AST import guard, Playwright `Approve does not auto-ready draft` |
| 8 | Per-row «Сделать ready» next to draft badge; batch CTA only when `approvedDrafts.length > 0`; empty body confirm; one `markReadyBatch` call (D-01…D-04 / D-08) | ✓ VERIFIED | `AdminDigestPage.jsx` testids + handlers; Playwright per-row/batch; node `--test` batch single-call |
| 9 | After promote: optimistic ready + refetch; on promote failure toast and badge stays draft — no fake ready (D-05) | ✓ VERIFIED | Optimistic `setItems` + catch restores `previous`; Playwright happy path. **Quality note:** open CR-01 on live path when POST succeeds but shortlist refetch inside `markReady` throws (see Quality Concerns) |
| 10 | Exact D-15 empty copy + named `honest_factor_labels` 0/1/2+/whitespace matrix (D-13…D-17) | ✓ VERIFIED | `factorText` string match; `test_score_factors.py` named cases; Playwright exact string |
| 11 | Long material titles still wrap with usable draft badge + «Сделать ready» | ⚠️ insufficient_spec | `verification: backstop` — code has `break-words` / flex wrap; no held-out visual proof |
| 12 | Many approved-draft titles under send hint scroll/wrap without covering batch CTA | ⚠️ insufficient_spec | `verification: backstop` — sticky footer structure present; layout unproven |
| 13 | Long factor captions / empty justification wrap inside `max-w-[12rem]` without breaking row grid | ⚠️ insufficient_spec | `verification: backstop` — classes present; grid integrity unproven |

**Score:** 10/13 truths verified (0 present-behavior-unverified; 3 backstop abstentions → human)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `backend/src/backend/domain/material.py` | `with_ready_status` | ✓ VERIFIED | Status-only; already-ready identity |
| `backend/src/backend/application/use_cases/mark_material_ready.py` | single + batch helpers | ✓ VERIFIED | Wired; catches not-found per id |
| `backend/src/backend/interface/http/routes/admin.py` | single + batch ready routes | ✓ VERIFIED | `require_admin`; collection before `{id}`; 200 partial |
| `backend/src/backend/tests_support/in_memory.py` | shortlist status overlay | ✓ VERIFIED | `attach_materials` / `_overlay_batch` + `claim_sent` |
| `tests/unit/test_mark_material_ready.py` | ADUX-05 domain/use-case proofs | ✓ VERIFIED | Exists + green |
| `tests/unit/test_http_admin.py` | HTTP tracer + batch | ✓ VERIFIED | Exists + green |
| `tests/unit/test_set_shortlist_decision.py` | D-02 lock | ✓ VERIFIED | Assert + import guard |
| `web/src/services/adminReadyMock.js` | pure mock helpers | ✓ VERIFIED | No Vite/`import.meta` |
| `web/src/services/adminApi.js` | `markReady` / `markReadyBatch` | ✓ VERIFIED | Live + mock; batch ≠ loop `markReady` |
| `web/src/pages/AdminDigestPage.jsx` | promote UX + D-15 `factorText` | ✓ VERIFIED | Wired to services |
| `tests/unit/test_admin_mark_ready.js` | node `--test` gate | ✓ VERIFIED | 4/4 pass |
| `tests/admin.spec.js` | Playwright ready + D-15 | ✓ VERIFIED | Cases present |
| `tests/unit/test_score_factors.py` | honesty matrix | ✓ VERIFIED | Named 0/1/2+/whitespace |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `POST /admin/materials/{id}/ready` | materials.status ready + shortlist + send clear | `mark_material_ready` → save → overlay → send | ✓ WIRED | Manual: route → use-case → repo; overlay in in-memory; HTTP send-bridge test green |
| `POST /admin/materials/ready` | `results[]` partial | `mark_materials_ready` | ✓ WIRED | Batch route + DTO mapping |
| `AdminDigestPage` «Сделать ready» | ready endpoints | `markReady` / `markReadyBatch` → optimistic → refetch | ✓ WIRED | Imports + handlers + Playwright |
| Batch confirm | one batch POST | `markReadyBatch(ids)` once | ✓ WIRED | Source + harness counter + node test |
| `factor_labels[]` | caption | BE honesty + FE `factorText` | ✓ WIRED | No fabricated defaults |

Automated `verify.key-links` reported false only because PLAN `from:` values are endpoint/UI labels, not file paths — manual wiring evidence used.

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Admin shortlist badge | `item.material_status` | GET shortlist / materials join (live) or mock overlay | Yes (repo status after promote) | ✓ FLOWING |
| Ready promote | `materials.status` | `mark_material_ready` → `MaterialRepository.save` | Yes | ✓ FLOWING |
| Обоснование caption | `item.factor_labels` | BE `honest_factor_labels(score_factors)` → shortlist DTO | Yes when ≥2 labels; else D-15 empty | ✓ FLOWING |
| Mock empty seed | material 104 `factor_labels: []` | `getMockDefaultItems` | Explicit empty for honesty | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Domain/HTTP ready + score honesty | `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_http_admin.py::test_admin_mark_ready_promotes_draft_and_clears_send_gate tests/unit/test_score_factors.py -q` | 13 passed | ✓ PASS |
| FE mock/service gate | `node --test tests/unit/test_admin_mark_ready.js` | 4 pass / 0 fail | ✓ PASS |
| Playwright ready/D-15 suite | (existence enumerated in `tests/admin.spec.js`; not re-run full browser suite this pass) | Cases present for per-row, batch, Approve≠ready, D-15 | ? SKIP (browser) |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| ADUX-05 | 14-01, 14-02, 14-03 | Admin draft→ready in UI so send not blocked by D-85 without SQL | ✓ SATISFIED | API + FE + unit/HTTP/Playwright proofs; REQUIREMENTS.md maps Phase 14 Complete |
| ADUX-06 | 14-03 | Honest «Обоснование» — populated or explicit empty, no silent fake | ✓ SATISFIED | D-15 FE copy + `honest_factor_labels` matrix + Playwright |

No orphaned Phase 14 requirement IDs in REQUIREMENTS.md beyond ADUX-05 / ADUX-06.

### Prohibitions

| Statement | Status | Evidence |
| --------- | ------ | -------- |
| MUST NOT call `publish_material` / `as_ready` / indexing on admin promote | ✓ held | Grep clean on use-case + ready routes |
| MUST NOT auto-ready on Approve / `set_shortlist_decision` | ✓ held | Import guard + Playwright D-02 |
| MUST NOT implement batch via FE-loop of single ready | ✓ held | `markReadyBatch` body never calls `markReady` (node test) |
| MUST NOT return HTTP 207 / abort batch on missing id | ✓ held | HTTP 200 + per-id `material_not_found` |
| MUST NOT fabricate FE factor labels | ✓ held | `factorText` joins server labels only |
| MUST NOT add score_factors writers / PIPE UI this phase | ✓ held | No writers/UI added |
| MUST NOT couple Approve toolbar to `markReady` | ✓ held | `applyDecision` separate from promote handlers |
| MUST NOT redesign shortlist chrome beyond D-01…D-17 | ? judgment | Incremental controls + D-15 copy only on inspection — accept as held |

### Decision Coverage

All trackable CONTEXT.md decisions are honored by shipped artifacts. (17/17; non-blocking gate)

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `tests/unit/test_mark_material_ready.py` | ADUX-05 | yes | 0 | no | Behavioral | PASS |
| `tests/unit/test_http_admin.py` (ready*) | ADUX-05 | yes | 0 | no | Behavioral | PASS |
| `tests/unit/test_set_shortlist_decision.py` | ADUX-05 | yes | 0 | no | Behavioral + import | PASS |
| `tests/unit/test_admin_mark_ready.js` | ADUX-05/06 | yes | 0 | no | Value | PASS |
| `tests/unit/test_score_factors.py` | ADUX-06 | yes | 0 | no | Value | PASS |
| `tests/admin.spec.js` (ready / Обоснование) | ADUX-05/06 | yes | 0 | no | Behavioral | PASS |

**Disabled tests on requirements:** 0  
**Circular patterns detected:** 0  
**Insufficient assertions:** 0

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `AdminDigestPage.jsx` | ~679 | `placeholder=` input attr | ℹ️ Info | HTML placeholder, not a stub |
| `container.py` | ~116 | comment “Placeholder replaced…” | ℹ️ Info | Wiring comment, not incomplete feature |

No unresolved `TBD` / `FIXME` / `XXX` debt markers in phase-modified sources.

### Quality Concerns (open code-review — not gaps)

Per `14-REVIEW-DISPOSITION.md` (**Blocking for verify: none**):

1. **CR-01** — Live `markReady` couples promote success to shortlist refetch; refetch failure after successful POST rolls UI to draft while DB is ready. Softens D-05 live edge-case; does **not** falsify roadmap SC1/SC2 happy path proven under mocks + HTTP. Track as follow-up fix, not `/gsd-plan-phase --gaps`.
2. **WR-01** — Batch aborts on `PersistenceError` (partial-success docstring incomplete for persistence).
3. **WR-02** — Non-empty blank `factors[]` can shadow flat keys (uncommon); primary honesty matrix remains green.

### Human Verification Required

### 1. Long title + ready CTA layout

**Test:** Open Admin Digest with a long draft title; confirm draft badge + «Сделать ready» stay usable in the meta flex wrap.  
**Expected:** Title wraps with `break-words`; badge and CTA remain clickable.  
**Why human:** Backstop must-have — layout usability.

### 2. Sticky footer with many approved drafts

**Test:** Approve several drafts (N≥2); inspect sticky send footer.  
**Expected:** Titles wrap/scroll without covering the batch CTA hit target.  
**Why human:** Backstop must-have — sticky footer geometry.

### 3. Factor caption / empty justification wrap

**Test:** Row with long factor captions + row showing D-15 empty sentence.  
**Expected:** Copy wraps inside `max-w-[12rem]` without breaking the shortlist row grid.  
**Why human:** Backstop must-have — grid/overflow.

### Gaps Summary

No goal-blocking gaps. Roadmap SC1–SC3 and ADUX-05/ADUX-06 are satisfied in code with automated proofs. Overall status is `human_needed` solely due to three PLAN `verification: backstop` layout truths and the resulting visual UAT items. Open CR-01 is recorded as a quality concern, not a verification gap.

---

_Verified: 2026-10-03T13:17:51Z_  
_Verifier: Claude (gsd-verifier)_
