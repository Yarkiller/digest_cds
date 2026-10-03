---
phase: 14-draft-ready-justification-honesty
verified: 2026-10-03T17:20:00Z
status: human_needed
score: 17/23 must-haves verified
covered_files:
  - .planning/phases/14-draft-ready-justification-honesty/14-01-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-01-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-02-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-02-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-03-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-03-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-04-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-04-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-05-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-05-SUMMARY.md
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
  - web/src/services/adminReadyReconcile.js
covered_digest: "v2:sha256:2282ab4bde8dd7694d17b9bbaee7760519931da8cc1ddfb0147e429381063f69"
behavior_unverified: 3
overrides_applied: 0
decision_coverage:
  honored: 17
  total: 17
  not_honored: []
re_verification:
  previous_status: human_needed
  previous_score: 10/13
  gaps_closed: []
  gaps_remaining: []
  regressions: []
  note: "Prior report (2026-10-03T13:17:51Z) was stale (#4682 — covered source changed after the verifier ran). Truth set re-derived from ROADMAP SCs + all five PLAN must_haves; 14-04/14-05 gap-closure truths added."
behavior_unverified_items:
  - truth: "After promote: optimistic ready + silent refetch; on promote failure toast and badge stays draft — no fake ready (D-05)"
    test: "Force a per-row «Сделать ready» failure (backend error) and observe the row"
    expected: "A toast is shown and the row rolls back to «черновик» (no fake ready)"
    why_human: "Rollback-on-failure state transition; no failure-injection exists for markReady (no armFailNextReady) and no test exercises the promote-failure branch — happy path only is Playwright-covered"
  - truth: "Batch partial: ok ids optimistic ready; failed ids toast + stay draft (D-08)"
    test: "Trigger a batch promote in which some material_ids fail, and observe the rows"
    expected: "ok ids become «готов»; failed ids stay «черновик» with a toast listing them"
    why_human: "Rollback of failed ids is a state transition; the batch Playwright case exercises only the all-ok path, and the node test covers the pure mock helper, not the page handler's failed-id rollback"
  - truth: "batch promote path applies the same no-clobber reconciliation to its ok ids (never silently reverts a confirmed batch promote)"
    test: "Force a stale batch refetch (backend acks POST /admin/materials/ready but the shortlist still reports draft) and observe the promoted ok ids"
    expected: "Promoted ok ids stay «готов» after the refetch"
    why_human: "14-REVIEW WR-03: the __DIGEST_ADMIN_STALE_READY__ harness is honoured only by the single markReady mock, so the batch preservePromotedReady(dto.items, [...okIds]) call is asserted only by a source-text regex — no behavioral test exercises the batch half of G-14-2"
coincidental_reliance_items: []
human_verification:
  - test: "Open Admin Digest with a long draft title; confirm draft badge + «Сделать ready» stay usable in the meta flex wrap"
    expected: "Title wraps with break-words; badge and CTA remain clickable without overflow clipping"
    why_human: "14-03 must_have marked verification: backstop — layout usability cannot be proven by unit/presence checks"
  - test: "Approve several drafts so N≥2; inspect the sticky send footer (now count-only hint + quantified batch CTA, no title list)"
    expected: "The count-only hint and «Сделать ready все одобренные черновики (N)» CTA remain visible and hit-testable without covering each other"
    why_human: "14-03 must_have marked verification: backstop — sticky footer hit-target geometry needs visual check (footer no longer re-lists titles per 14-05 G-14-2b)"
  - test: "View a shortlist row with long factor captions and a row with empty Обоснование"
    expected: "Long captions and the D-15 empty sentence wrap with break-words inside max-w-[12rem] without breaking the shortlist row grid"
    why_human: "14-03 must_have marked verification: backstop — grid/overflow behavior is visual"
---

# Phase 14: Draft→ready & justification honesty Verification Report

**Phase Goal:** Admin can unblock send without SQL and see honest shortlist justification
**Verified:** 2026-10-03T17:20:00Z
**Status:** human_needed
**Re-verification:** Yes — regenerated because the prior report (2026-10-03T13:17:51Z, 10/13) was stale; source changed after UAT-driven gap closure (14-04, 14-05).

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | Admin can set a material from draft → ready in the admin UI without a direct SQL workaround (roadmap SC1 / ADUX-05) | ✓ VERIFIED | `AdminDigestPage` `admin-mark-ready` / `admin-mark-ready-batch` handlers → `adminApi.markReady` / `markReadyBatch` → `POST /admin/materials/{id}/ready` and `POST /admin/materials/ready`. Playwright `per-row Сделать ready promotes draft and clears draft hint` and `batch … issues one markReadyBatch` **PASS** this pass |
| 2 | After promotion, D-85 send gate no longer blocks that material solely for still being draft (roadmap SC2 / ADUX-05) | ✓ VERIFIED | `test_admin_mark_ready_promotes_draft_and_clears_send_gate` green; Playwright stale/per-row tests assert the draft hint clears after promote |
| 3 | Shortlist «Обоснование» shows populated score_factors or an explicit empty/unavailable state — never silent fake (roadmap SC3 / ADUX-06) | ✓ VERIFIED | `factorText` returns exact D-15 empty string for <2 labels; populated joins server `factor_labels` only; `honest_factor_labels` matrix green; Playwright asserts the exact string. Narrow non-string-label edge recorded as a quality concern (WR-01), not a covered-shape failure |
| 4 | Status-only promote leaves `published_at` unchanged and never routes through `publish_material` / `Material.as_ready` (D-06) | ✓ VERIFIED | `Material.with_ready_status` (`material.py`) uses `replace` with no `assert_publishable`; `mark_material_ready` and the ready routes have no publish/index imports; unit `test_mark_material_ready_empty_body_draft_sets_ready_leaves_published_at` green |
| 5 | Already-ready promote returns 200 no-op; empty body still promotes; missing material → 404 `material_not_found` (D-09 / D-10) | ✓ VERIFIED | `test_mark_material_ready_already_ready_is_noop`, `test_admin_mark_ready_already_ready_is_noop`, missing-id 404 unit + Playwright soft-warn path |
| 6 | Batch `POST /admin/materials/ready` returns HTTP 200 order-preserving partial success; `extra=forbid`; empty ids → `results=[]` (D-08) | ✓ VERIFIED | `mark_materials_ready` (order-preserving, per-id `material_not_found`, per-id `PersistenceError`); `MarkReadyBatch*` `extra=forbid`; HTTP `partial_success` / `empty_ids` / `unknown_field_422` / employee 403 tests green |
| 7 | Approve on draft leaves `material_status` draft — approve ≠ ready (D-02) | ✓ VERIFIED | `test_approve_allowed_on_draft_material` + AST import guard + Playwright `Approve does not auto-ready draft (D-02)` asserts «одобрен (в шортлист)» + «черновик» coexist |
| 8 | Per-row «Сделать ready» sits next to the draft badge and hides once ready; batch CTA only when `approvedDrafts.length > 0`; confirm with count N; one `markReadyBatch` call (D-01…D-04 / D-08) | ✓ VERIFIED | `AdminDigestPage.jsx` testids + handlers; Playwright per-row/batch green; harness counter asserts exactly one batch call; node `--test` batch single-call |
| 9 | After promote: optimistic ready + silent refetch; on promote failure toast and badge stays draft — no fake ready (D-05) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Optimistic `setItems` + best-effort refetch are Playwright-proven (happy path), and `catch { setItems(previous); setToast(...) }` is present — but no failure-injection exists for `markReady` and no test exercises the rollback path. See Human Verification |
| 10 | Batch partial: ok ids optimistic ready; failed ids toast + stay draft (D-08) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `promoteApprovedDrafts` maps `failedIds` back to prior status + toasts; the pure `applyMockMarkReadyBatch` helper is unit-tested, but no test drives the page handler's failed-id rollback. See Human Verification |
| 11 | Exact D-15 empty «Обоснование» copy + populated server-only join + named `honest_factor_labels` 0/1/2+/whitespace matrix (D-13…D-17; ADUX-06) | ✓ VERIFIED | `factorText` exact-string match; `test_score_factors.py` named cases green; Playwright exact D-15 assert |
| 12 | Long material titles still wrap with usable draft badge + «Сделать ready» | ⚠️ insufficient_spec (backstop) | `verification: backstop` — `break-words` / flex wrap present; no held-out visual proof |
| 13 | Many approved-draft titles under the send hint scroll/wrap without covering batch CTA | ⚠️ insufficient_spec (backstop) | `verification: backstop` — footer is now count-only (no title list) after 14-05; geometry still visually unproven |
| 14 | Long factor captions / empty justification wrap inside `max-w-[12rem]` without breaking row grid | ⚠️ insufficient_spec (backstop) | `verification: backstop` — classes present; grid integrity unproven |
| 15 | G-14-2: per-row «Сделать ready» stays ready even when the post-POST shortlist refetch still reports draft (silent revert eliminated) | ✓ VERIFIED | `preservePromotedReady` forces promoted ids; Playwright `stale still-draft refetch does not revert a promoted row (G-14-2)` **PASS** this pass; node unit suite green |
| 16 | G-14-2: `markReady` (live) POSTs `/admin/materials/{id}/ready` and treats `MarkReadyResponse` as source of truth — no `fetchShortlist` coupling | ✓ VERIFIED | `adminApi.js` `markReady` body contains no `fetchShortlist`; returns `response.json()` (live) / `{material_id, status:'ready'}` (mock); node source-shape test green |
| 17 | G-14-2: a still-draft refetch is reconciled best-effort — promoted ids stay ready, other rows follow the refetch | ✓ VERIFIED | Pure helper unit suite (still-draft→ready, identity when already ready, multi-id, null/empty safe); both handlers wrap `refreshed.items` through `preservePromotedReady` |
| 18 | G-14-2: batch promote path applies the same no-clobber reconciliation to its ok ids (never silently reverts a confirmed batch promote) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `promoteApprovedDrafts` calls `preservePromotedReady(dto.items, [...okIds])`, but the stale harness is single-path only; only a source-text regex asserts this branch (14-REVIEW WR-03). See Human Verification |
| 19 | G-14-2: a harness flag simulates a backend that acknowledges the POST but does not persist | ✓ VERIFIED | `__DIGEST_ADMIN_STALE_READY__` arms `markReady` mock skip-persist; cleared in `resetAdminHarness`; used by the Playwright stale test |
| 20 | G-14-2a: an approved draft no longer reads as a contradiction — two disambiguated axes | ✓ VERIFIED | Playwright D-02 case asserts «черновик» + «одобрен (в шортлист)» coexist on the approved draft row |
| 21 | G-14-2a: `material_status` pill localised («черновик»/«готов»); decision caption qualified («одобрен (в шортлист)»/«отклонён (из шортлиста)») | ✓ VERIFIED | `materialStatusLabel` + `decisionCaption`; pill renders `materialStatusLabel(item.material_status)`; no raw English `draft`/`ready` pill remains |
| 22 | G-14-2b: sticky send footer no longer re-lists approved-draft titles | ✓ VERIFIED | Footer renders only `admin-send-hint` + batch CTA (no `<ul>`); Playwright asserts footer `ul` count 0 |
| 23 | G-14-2b: batch CTA label quantified «Сделать ready все одобренные черновики (N)» | ✓ VERIFIED | `AdminDigestPage.jsx` interpolates `approvedDrafts.length`; Playwright asserts `…(1)` for N=1 |

**Score:** 17/23 truths verified (3 present, behavior-unverified; 3 backstop abstentions → human)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `backend/src/backend/domain/material.py` | `with_ready_status` | ✓ VERIFIED | Status-only; already-ready identity; `published_at` untouched |
| `backend/src/backend/domain/shortlist.py` | `honest_factor_labels` | ✓ VERIFIED | ≥2 readable labels or `[]`; flat-key fallback (WR-02); non-string-label edge open (WR-01) |
| `backend/src/backend/application/use_cases/mark_material_ready.py` | single + batch helpers | ✓ VERIFIED | Wired; per-id not-found/persistence errors; `except Exception` catch-all (IN-04) |
| `backend/src/backend/interface/http/routes/admin.py` | single + batch ready routes | ✓ VERIFIED | `require_admin`; collection before `{id}`; 200 partial; `extra=forbid` |
| `backend/src/backend/tests_support/in_memory.py` | shortlist status overlay | ✓ VERIFIED | overlays material_status from attached materials repo |
| `web/src/services/adminReadyReconcile.js` | pure `preservePromotedReady` | ✓ VERIFIED | Node-safe; identity-preserving |
| `web/src/services/adminApi.js` | `markReady` / `markReadyBatch` | ✓ VERIFIED | Decoupled; stale harness flag |
| `web/src/pages/AdminDigestPage.jsx` | promote UX + reconciled refetch + localised axes | ✓ VERIFIED | Imports `preservePromotedReady`; both handlers reconcile |
| `tests/unit/test_admin_mark_ready.js` | node `--test` gate | ✓ VERIFIED | 10 pass / 0 fail this pass |
| `tests/admin.spec.js` | Playwright ready + stale + honesty | ✓ VERIFIED | Phase-relevant subset 6 passed this pass |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `POST /admin/materials/{id}/ready` | materials.status ready + shortlist status + send clear | `mark_material_ready` → `MaterialRepository.save` → overlay → `send_digest` | ✓ WIRED | HTTP send-bridge test green |
| `POST /admin/materials/ready` | `results[]` partial | `mark_materials_ready` | ✓ WIRED | Batch route + DTO mapping; 200 partial tests green |
| `AdminDigestPage` «Сделать ready» | ready endpoints | `markReady` / `markReadyBatch` → optimistic → refetch reconciled by `preservePromotedReady` | ✓ WIRED | Imports + handlers; Playwright single-path stale proof green |
| Batch refetch | `preservePromotedReady(dto.items, [...okIds])` | `promoteApprovedDrafts` | ⚠️ PARTIAL | Wiring present but behavior not exercised (WR-03 / truth 18) |
| `material_status` pill + `decisionCaption` | shortlist row meta container | `materialStatusLabel` / `decisionCaption` | ✓ WIRED | Playwright disambiguation asserts green |
| `factor_labels[]` | caption | BE honesty + FE `factorText` | ✓ WIRED | No fabricated defaults |

Automated `verify.key-links` reports false only because PLAN `from:` values are endpoint/UI labels, not file paths — manual wiring evidence used.

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Admin shortlist badge | `item.material_status` | GET shortlist / materials join (live) or mock overlay | Yes | ✓ FLOWING |
| Ready promote | `materials.status` | `mark_material_ready` → `MaterialRepository.save` | Yes | ✓ FLOWING |
| Post-promote reconcile | `refreshed.items` → `preservePromotedReady` | `fetchShortlist()` refetch wrapped before `applyBatch` | Yes (single path proven; batch path source-asserted only) | ⚠️ PARTIAL (batch) |
| Обоснование caption | `item.factor_labels` | BE `honest_factor_labels` → shortlist DTO | Yes when ≥2 string labels; else D-15 empty | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| FE pure helper + reconcile wiring | `node --test tests/unit/test_admin_mark_ready.js` | 10 pass / 0 fail | ✓ PASS |
| Domain/use-case + honesty matrix + D-02 lock | `uv run pytest tests/unit/test_mark_material_ready.py tests/unit/test_score_factors.py tests/unit/test_set_shortlist_decision.py -q` | 22 passed | ✓ PASS |
| HTTP ready + batch + decision | `uv run pytest tests/unit/test_http_admin.py -k "ready or decision or draft" -q` | 17 passed, 14 deselected | ✓ PASS |
| Phase Playwright (incl. G-14-2 stale, G-14-2a/2b, D-02) | `npx playwright test --project=web tests/admin.spec.js -g "stale still-draft\|per-row\|batch Сделать\|Approve does not auto-ready\|approved draft blocks send\|populated shortlist"` | 6 passed | ✓ PASS |
| Full `tests/admin.spec.js` | `npx playwright test --project=web tests/admin.spec.js` | 10 passed then `ERR_CONNECTION_REFUSED` (dev server dropped mid-run — environment, not assertion failure) | ? SKIP (environment) |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| ADUX-05 | 14-01, 14-02, 14-03, 14-04, 14-05 | Admin sets material draft→ready in UI so send is not blocked by D-85 without SQL | ✓ SATISFIED | API + FE + unit/HTTP/Playwright (incl. stale-refetch lock); REQUIREMENTS.md maps Phase 14 Complete |
| ADUX-06 | 14-03 | Honest «Обоснование» — populated or explicit empty, no silent fake | ✓ SATISFIED | D-15 FE copy + `honest_factor_labels` matrix + Playwright exact; narrow non-string-label edge is WR-01 (quality concern) |

No orphaned Phase 14 requirement IDs beyond ADUX-05 / ADUX-06.

### Prohibitions

| Statement | Verdict | Evidence |
| --------- | ------- | -------- |
| MUST NOT call `publish_material` / `as_ready` / `assert_publishable` / indexing on admin promote | ✓ held | Grep clean on `mark_material_ready.py` + ready routes |
| MUST NOT auto-ready on Approve / `set_shortlist_decision` | ✓ held | Import guard + Playwright D-02 |
| MUST NOT implement batch via FE-loop of single ready | ✓ held | `markReadyBatch` body never calls `markReady` (node test) |
| MUST NOT return HTTP 207 / abort batch on missing id | ✓ held | HTTP 200 + per-id `material_not_found` |
| MUST NOT fabricate FE factor labels | ✓ held (narrow BE edge open) | `factorText` joins server labels only; BE non-string label stringified — WR-01 quality concern |
| MUST NOT add score_factors writers / PIPE UI this phase | ✓ held | No writers/UI added |
| MUST NOT couple Approve toolbar to `markReady` | ✓ held | `applyDecision` separate from promote handlers |
| MUST NOT redesign shortlist chrome beyond D-01…D-17 | ? judgment | Incremental copy/control changes only on inspection — accept as held |

### Decision Coverage

All trackable CONTEXT.md decisions D-01…D-17 are honored by shipped artifacts. (17/17; non-blocking gate)

## Quality Concerns (open code-review — not gaps)

Per `14-REVIEW.md` (0 critical, 3 warnings, 4 info) and `14-REVIEW-DISPOSITION.md` (all 8 rows `open`; prior CR-01 carried as `fixed`):

- **CR-01 — RESOLVED (verified).** Live `markReady` no longer calls `fetchShortlist`; the `MarkReadyResponse` is the authoritative promote result (truth 16), and a still-draft refetch is reconciled by `preservePromotedReady` (truths 15/17). The G-14-2 class is fixed on the single-promote path.
- **WR-02 (open, warning).** Live `markReady` still `return response.json()` without guarding parse failure (`adminApi.js` ~396). A 2xx with an unparseable body would throw and re-trigger the rollback path — a residual silent-revert class relocated to the parse boundary. Related to truth 9 (behavior-unverified).
- **WR-03 (open, warning).** Batch reconcile is regression-unlocked (source-text assertion only) — surfaced as truth 18, behavior-unverified, human verification.
- **WR-01 (open, warning).** `honest_factor_labels` stringifies non-string labels: reproduced `{'label': None}`→`['None','None']`, `{'label':1}`→`['1','2']`. Narrow honesty edge for an unusual stored shape; the shipped 0/1/2+/whitespace matrix is green, so recorded as a quality concern (not a gap). Suggested follow-up: accept only `isinstance(label, str)`.
- **IN-01…IN-04 (open, info).** Source-text wiring assertions; weak footer `ul` proxy; unbounded batch `material_ids`; broad `except Exception` in the batch helper. Non-blocking.
- **Note:** `14-REVIEW-DISPOSITION.md` "Dropped on this run" line explains that WR-01/WR-02 were previously `fixed` then reused by new findings with the same ids — the current open warnings are the new findings, not the old fixed ones.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `AdminDigestPage.jsx` | ~705 | `placeholder=` input attr | ℹ️ Info | HTML placeholder, not a stub |
| — | — | No `TBD` / `FIXME` / `XXX` debt markers in phase-modified sources (verified by grep) | — | None |

### Human Verification Required

#### 1. Long title + ready CTA layout

**Test:** Open Admin Digest with a long draft title; confirm draft badge + «Сделать ready» stay usable in the meta flex wrap.
**Expected:** Title wraps with `break-words`; badge and CTA remain clickable.
**Why human:** Backstop must-have — layout usability.

#### 2. Sticky footer with many approved drafts

**Test:** Approve several drafts (N≥2); inspect the sticky send footer (now count-only hint + quantified CTA, no title list).
**Expected:** The count-only hint and «Сделать ready все одобренные черновики (N)» CTA remain visible and hit-testable.
**Why human:** Backstop must-have — sticky footer geometry (footer no longer re-lists titles per G-14-2b).

#### 3. Factor caption / empty justification wrap

**Test:** Row with long factor captions + row showing the D-15 empty sentence.
**Expected:** Copy wraps inside `max-w-[12rem]` without breaking the shortlist row grid.
**Why human:** Backstop must-have — grid/overflow.

#### 4. Per-row promote failure rollback (truth 9)

**Test:** Force a per-row «Сделать ready» failure (backend error) and observe the row.
**Expected:** A toast is shown and the row rolls back to «черновик» (no fake ready).
**Why human:** Rollback-on-failure state transition; no failure-injection for `markReady` and no test exercises the failure branch.

#### 5. Batch promote partial failure (truth 10)

**Test:** Trigger a batch promote in which some ids fail; observe the rows.
**Expected:** ok ids become «готов»; failed ids stay «черновик» with a toast listing them.
**Why human:** Rollback of failed ids is a state transition; only the all-ok batch path is Playwright-covered.

#### 6. Batch stale-refetch no-clobber (truth 18 / WR-03)

**Test:** Force a stale batch refetch (backend acks the batch POST but the shortlist still reports draft); observe the promoted ok ids.
**Expected:** Promoted ok ids stay «готов» after the refetch.
**Why human:** The stale harness only covers the single markReady mock; the batch `preservePromotedReady` branch has no behavioral test.

### Gaps Summary

No goal-blocking gaps. Roadmap SC1–SC3 and ADUX-05/ADUX-06 hold in code with automated proofs, and the G-14-2 blocker (per-row silent revert under a still-draft refetch) is genuinely resolved and regression-locked at both unit and Playwright layers; G-14-2a and G-14-2b are shipped and asserted. Overall status is `human_needed` because of three PLAN `verification: backstop` layout truths plus three behavior-dependent truths whose rollback/invariant paths have no behavioral test (truths 9, 10, 18 — the last aligning with 14-REVIEW WR-03). Open review warnings WR-01/WR-02 are recorded as quality concerns, not gaps.

---

_Verified: 2026-10-03T17:20:00Z_
_Verifier: Claude (gsd-verifier)_
