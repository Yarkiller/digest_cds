---
phase: 14-draft-ready-justification-honesty
verified: 2026-10-03T18:55:00Z
status: human_needed
score: 19/20 must-haves verified
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
  - .planning/phases/14-draft-ready-justification-honesty/14-06-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-06-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-07-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-07-SUMMARY.md
  - .planning/phases/14-draft-ready-justification-honesty/14-08-PLAN.md
  - .planning/phases/14-draft-ready-justification-honesty/14-08-SUMMARY.md
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
covered_digest: "v2:sha256:550542ba8c8fabda1fa621b054ef7c5c51c3990f3b75ff51de300c31621995e9"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 17/23
  gaps_closed:
    - "G-14-1 / G-14-4: SupabaseMaterialRepository._fetch_one ambiguous material_relations embed (PGRST201 → PersistenceError → live HTTP 503 on POST /admin/materials/{id}/ready and all live reads) — disambiguated by FK hint (plan 14-06)"
    - "G-14-2: admin footer batch promote CTA (admin-mark-ready-batch) + the «Уберите черновики из одобренных или дождитесь ready.» hint removed; sendHint reordered (plan 14-07)"
    - "G-14-3: interactive admin controls (incl. «Превью материала») now show a pointer cursor via a global base rule + computed-cursor Playwright lock (plan 14-08)"
  gaps_remaining: []
  regressions: []
  superseded:
    - "Prior truth: batch partial promote rollback (D-08) — FE batch affordance removed by operator override (14-07); backend batch path retained but unhooked, still HTTP-covered"
    - "Prior truth: batch stale-refetch no-clobber reconcile (14-04 must_have #4) — no FE batch caller remains"
    - "Prior truth: sticky-footer batch-CTA geometry backstop (14-03) — batch CTA removed"
human_verification:
  - test: "Re-run the live per-row «Сделать ready» on real Supabase data (live mode, VITE_USE_MOCKS=false) on a draft material with a non-empty body"
    expected: "POST /admin/materials/{id}/ready returns 200 (not 503) and the row badge flips to «готов» after the silent refetch"
    why_human: "The G-14-1 root cause was a live-only PostgREST embed failure; the offline regression simulates the PGRST201 rejection, and the executor's live read probe was not re-run by the verifier (no independent network access)"
  - test: "Open Admin Digest with a long draft title; confirm the draft badge and «Сделать ready» stay usable in the meta flex wrap"
    expected: "Title wraps with break-words; badge and CTA remain clickable without overflow clipping"
    why_human: "14-03 must-have marked verification: backstop — layout usability cannot be proven by unit/presence checks; UAT test 1 exercised the row but recorded the (now-fixed) backend 503, not the layout"
---

# Phase 14: Draft→ready & justification honesty Verification Report

**Phase Goal:** Admin can unblock send without SQL and see honest shortlist justification
**Verified:** 2026-10-03T18:55:00Z
**Status:** human_needed
**Re-verification:** Yes — after gap-closure plans 14-06, 14-07, 14-08 (G-14-1/2/3/4)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | SC1 / ADUX-05: Admin can set a material `draft` → `ready` in the admin UI without a direct SQL workaround | ✓ VERIFIED | `AdminDigestPage` `admin-mark-ready` → `adminApi.markReady` → `POST /admin/materials/{id}/ready`; Playwright `per-row Сделать ready promotes draft and clears draft hint (ADUX-05)` and `stale still-draft refetch … (G-14-2)` **PASS** this pass (36/36 admin suite) |
| 2 | SC2 / ADUX-05: after promotion the D-85 send gate no longer blocks that material solely for still being draft | ✓ VERIFIED | `test_admin_mark_ready_promotes_draft_and_clears_send_gate` green (independently run); Playwright asserts the draft hint clears after promote |
| 3 | SC3 / ADUX-06: shortlist «Обоснование» shows populated `score_factors` or an explicit empty state — never a silent fake | ✓ VERIFIED | `factorText` returns the exact D-15 empty string for <2 labels, joins server labels only; `tests/unit/test_score_factors.py` named 0/1/2+/whitespace matrix green; Playwright asserts the exact string |
| 4 | D-06: status-only promote leaves `published_at` unchanged and never routes through `publish_material` / `Material.as_ready` | ✓ VERIFIED | `Material.with_ready_status` (`material.py:48`) uses `replace(status=READY, updated_at=now)` with no `assert_publishable`; `mark_material_ready.py` imports no publish/index path |
| 5 | D-09 / D-10: already-ready promote is a 200 no-op; empty body still promotes; missing material → 404 `material_not_found` | ✓ VERIFIED | `test_admin_mark_ready_already_ready_is_noop`, `test_admin_mark_ready_missing_material_returns_404` green |
| 6 | D-08: batch `POST /admin/materials/ready` returns HTTP 200 order-preserving partial success; `extra=forbid`; empty ids → `results=[]` | ✓ VERIFIED | `test_admin_mark_ready_batch_partial_success_preserves_order` / `_empty_ids_returns_empty_results` / `_unknown_field_returns_422` green (backend contract retained but unhooked from FE per 14-07) |
| 7 | D-02: Approve on a draft leaves `material_status` draft — approve ≠ ready | ✓ VERIFIED | Playwright `Approve does not auto-ready draft (D-02)` PASS; import guard test green |
| 8 | D-01: per-row «Сделать ready» sits next to the draft badge and hides once ready | ✓ VERIFIED | `admin-mark-ready` testid in the row meta; Playwright per-row + stale tests assert it disappears after promote |
| 9 | D-05: after promote optimistic ready + silent refetch; on failure a toast and the badge stays draft — no fake ready | ✓ VERIFIED | Optimistic `setItems` + reconciled refetch present and Playwright-proven; the rollback-on-failure branch is **UAT test 4 pass** (live: toast «Не удалось сделать ready», badge stayed «черновик») |
| 10 | G-14-2 (14-04): a still-draft refetch never silently reverts a promoted row | ✓ VERIFIED | Playwright `stale still-draft refetch does not revert a promoted row (G-14-2)` PASS; `__DIGEST_ADMIN_STALE_READY__` harness honoured by the `markReady` mock |
| 11 | G-14-2 (14-04): live `markReady` POSTs `/admin/materials/{id}/ready` and treats `MarkReadyResponse` as source of truth — no `fetchShortlist` coupling | ✓ VERIFIED | `adminApi.js` `markReady` body has no `fetchShortlist`; `return response.json()` (live) / `{material_id,status:'ready'}` (mock); node source-shape test green |
| 12 | G-14-2 (14-04): a still-draft refetch is reconciled best-effort via `preservePromotedReady` | ✓ VERIFIED | Pure helper unit suite (still-draft→ready, identity when ready, multi-id, null/empty safe) green; `promoteReady` wraps `refreshed.items` |
| 13 | 14-07: the footer offers no batch promote (CTA + handler + import gone) and the «Уберите черновики…» hint renders in no state; per-row control + D-85 gate intact | ✓ VERIFIED | No `admin-mark-ready-batch` / `promoteApprovedDrafts` / `markReadyBatch` in `AdminDigestPage.jsx`; `sendHint` branch order `… → «Отправка недоступна.»`; `sendUnlocked` still requires `approvedDrafts.length === 0`; Playwright `no batch promote CTA is rendered (G-14-2)` PASS; node source-shape lock green |
| 14 | G-14-2a (14-05): the approved-draft row reads as two disambiguated axes | ✓ VERIFIED | `materialStatusLabel` («черновик»/«готов») + `decisionCaption` («одобрен (в шортлист)»); Playwright D-02 case asserts both coexist |
| 15 | G-14-2b (14-05): the sticky send footer no longer re-lists approved-draft titles | ✓ VERIFIED | Footer renders only `admin-send-hint` + buttons (no `<ul>`); Playwright asserts footer `ul` count 0 |
| 16 | D-13…D-17 / ADUX-06: exact D-15 empty copy + populated server-only join + named `honest_factor_labels` 0/1/2+/whitespace matrix | ✓ VERIFIED | `factorText` exact string `Обоснование недоступно — скоринг не запускался`; `test_score_factors.py` named cases green |
| 17 | G-14-1 / G-14-4 (14-06): `_fetch_one` uses an FK-disambiguated `material_relations!material_relations_from_material_id_fkey(to_material_id)` embed so live `get()` / `get_by_slug()` return a `Material` (no PGRST201 → 503) | ✓ VERIFIED | `material_repository.py:135` emits the hinted embed; `001_initial_schema.sql:117` defines `from_material_id` (Postgres default constraint name matches the hint); offline PGRST201 regression green; executor live read probe recorded `get(2)=ready rag-systems` |
| 18 | G-14-1 (14-06): an offline regression fails on the bare embed and passes only after disambiguation; `material_tags` stays unhinted | ✓ VERIFIED | `tests/unit/test_supabase_material_repository_embed.py` 3 passed (independently run); asserts `material_relations!` present, bare `material_relations(to_material_id)` absent, `material_tags(...)` unhinted |
| 19 | G-14-3 (14-08): interactive admin controls show `cursor: pointer`, disabled buttons excluded, locked by a computed-cursor assertion | ✓ VERIFIED | `index.css` `@layer base { button:not(:disabled) { cursor: pointer } }`; Playwright `interactive admin controls show a pointer cursor (G-14-3)` PASS (audited controls + disabled Send guard) |
| 20 | 14-03 backstop: long material titles still wrap with usable draft badge + «Сделать ready» | ⚠️ insufficient_spec (backstop) | `break-words` / flex wrap present; `verification: backstop` — no held-out visual proof. See Human Verification |

**Score:** 19/20 truths verified (0 present-behavior-unverified; 1 backstop abstention → human)

### Superseded Must-Haves (operator override, plan 14-07)

| Prior truth | Disposition |
| ----------- | ----------- |
| Batch partial promote: ok ids ready, failed ids toast + stay draft (D-08) | FE batch affordance removed; backend batch path retained but unhooked and HTTP-covered |
| Batch promote path applies the same no-clobber reconcile to its ok ids | No FE batch caller remains |
| Sticky-footer batch-CTA geometry backstop | Batch CTA removed |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `supabase-integration/src/supabase_integration/material_repository.py` | Disambiguated relations embed in `_fetch_one` | ✓ VERIFIED | `material_relations!material_relations_from_material_id_fkey(to_material_id)`; tags unhinted |
| `tests/unit/test_supabase_material_repository_embed.py` | Offline PGRST201 regression (get/get_by_slug + embed shape) | ✓ VERIFIED | 3 tests pass |
| `web/src/pages/AdminDigestPage.jsx` | Batch CTA/handler/import removed; coherent `sendHint`; per-row retained | ✓ VERIFIED | No batch testid/handler/import; D-85 gate intact |
| `web/src/index.css` | Global `button:not(:disabled){cursor:pointer}` base rule | ✓ VERIFIED | Present at L37-40 |
| `tests/admin.spec.js` | Playwright G-14-2 removal + G-14-3 cursor locks | ✓ VERIFIED | `no batch promote CTA is rendered (G-14-2)`, `interactive admin controls show a pointer cursor (G-14-3)` PASS |
| `tests/unit/test_admin_mark_ready.js` | node `--test` reconcile + batch-removal source-shape lock | ✓ VERIFIED | 10 pass / 0 fail |
| `web/src/services/adminApi.js` | `markReady` decoupled from refetch; stale harness flag | ✓ VERIFIED | No `fetchShortlist` in `markReady`; `return response.json()` |
| `web/src/services/adminReadyReconcile.js` | Pure `preservePromotedReady` | ✓ VERIFIED | Identity-preserving; node suite green |
| `backend/src/backend/domain/material.py` | `with_ready_status` status-only transition | ✓ VERIFIED | No publish gate; `published_at` untouched |
| `backend/src/backend/domain/shortlist.py` | `honest_factor_labels` | ✓ VERIFIED | exact string for <2 labels; 0/1/2+/whitespace matrix green |
| `backend/src/backend/application/use_cases/mark_material_ready.py` | single + batch helpers | ✓ VERIFIED | status-only; per-id errors |
| `backend/src/backend/interface/http/routes/admin.py` | ready routes | ✓ VERIFIED | `require_admin`; batch before `{id}`; `extra=forbid` |
| `backend/src/backend/tests_support/in_memory.py` | shortlist status overlay | ✓ VERIFIED | Overlays `material_status` from the materials repo |
| `tests/unit/test_score_factors.py` | named honesty matrix | ✓ VERIFIED | 0/1/2+/whitespace cases green |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `AdminDigestPage` «Сделать ready» | `POST /admin/materials/{id}/ready` | `markReady` (source of truth) → optimistic → reconciled refetch | ✓ WIRED | Playwright stale + per-row proof green |
| `SupabaseMaterialRepository._fetch_one` | PostgREST `materials` embed | `material_relations!<fk>(to_material_id)` | ✓ WIRED | Offline PGRST201 regression green |
| native `<button>` (admin) | `index.css` `@layer base` | `button:not(:disabled){cursor:pointer}` | ✓ WIRED | Computed-cursor Playwright green |
| approved draft | `admin-send-footer` | `sendHint` neutral lock; no batch CTA; `sendUnlocked` D-85 | ✓ WIRED | Playwright D-85 + no-batch tests green |
| `factor_labels[]` | `factorText` caption | BE `honest_factor_labels` → shortlist DTO | ✓ WIRED | No fabricated defaults |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Admin shortlist badge | `item.material_status` | GET shortlist / materials join (live) or mock overlay | Yes | ✓ FLOWING |
| Ready promote | `materials.status` | `mark_material_ready` → `MaterialRepository.save` | Yes | ✓ FLOWING |
| Post-promote reconcile | `refreshed.items` → `preservePromotedReady` | `fetchShortlist()` refetch wrapped before `applyBatch` | Yes | ✓ FLOWING |
| Обоснование caption | `item.factor_labels` | BE `honest_factor_labels` → shortlist DTO | Yes when ≥2 string labels; else D-15 empty | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Offline PGRST201 embed regression | `uv run pytest tests/unit/test_supabase_material_repository_embed.py -q` | 3 passed | ✓ PASS |
| FE reconcile + batch-removal source lock | `node --test tests/unit/test_admin_mark_ready.js` | 10 pass / 0 fail | ✓ PASS |
| Domain/use-case + honesty matrix + D-02 lock | `uv run pytest tests/unit/test_supabase_issue_repository_contract.py tests/unit/test_mark_material_ready.py tests/unit/test_score_factors.py tests/unit/test_set_shortlist_decision.py -q` | 31 passed | ✓ PASS |
| Admin HTTP ready + draft | `uv run pytest tests/unit/test_http_admin.py -k "ready or draft" -q` | 11 passed, 20 deselected | ✓ PASS |
| Admin Playwright (full file incl. G-14-2/G-14-3) | `npm run test:web -- tests/admin.spec.js` | 36 passed / 0 failed (1.4m) | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| ADUX-05 | 14-01…14-08 | Admin sets material `draft`→`ready` in UI so send is not blocked by D-85 without SQL | ✓ SATISFIED | API + FE + unit/HTTP/Playwright (incl. stale-refetch lock + live read heal) |
| ADUX-06 | 14-03 | Honest «Обоснование» — populated or explicit empty, no silent fake | ✓ SATISFIED | D-15 FE copy + `honest_factor_labels` matrix + Playwright exact assert |

No orphaned Phase 14 requirement IDs beyond ADUX-05 / ADUX-06 (REQUIREMENTS.md maps both to Phase 14).

### Prohibitions

| Statement | Verdict | Evidence |
| --------- | ------- | -------- |
| MUST NOT call `publish_material` / `as_ready` / `assert_publishable` / indexing on admin promote | ✓ held | `with_ready_status` + `mark_material_ready.py` grep clean |
| MUST NOT auto-ready on Approve / `set_shortlist_decision` | ✓ held | Import guard + Playwright D-02 |
| MUST NOT implement batch via a FE-loop of single ready | ✓ held | `markReadyBatch` body never calls `markReady` (node test); FE no longer calls the batch path |
| MUST NOT return HTTP 207 / abort batch on missing id | ✓ held | HTTP 200 + per-id `material_not_found` |
| MUST NOT fabricate FE factor labels | ✓ held | `factorText` joins server labels only |
| MUST NOT add `score_factors` writers / PIPE UI this phase | ✓ held | No writers/UI added |
| MUST NOT couple Approve toolbar to `markReady` | ✓ held | `applyDecision` separate from promote handlers |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `web/src/services/adminApi.js` | 611 | Residual «Уберите черновики из одобренных или дождитесь ready.» copy inside a thrown `AdminApiError` | ℹ️ Info | Not rendered: the `DRAFT_IN_SEND_POOL` branch is unreachable via the UI (Send is disabled while an approved draft exists), and `confirmSend` maps send errors to the generic banner «Рассылка не отправлена». The rendered footer hint is gone as required |
| phase-modified sources | — | No `TBD` / `FIXME` / `XXX` debt markers (grep) | — | None |

### Human Verification Required

#### 1. Live per-row promote (G-14-1 live re-check)

**Test:** On live Supabase data (`VITE_USE_MOCKS=false`), promote a draft material with a non-empty body via per-row «Сделать ready».
**Expected:** `POST /admin/materials/{id}/ready` returns 200 (not 503) and the badge flips to «готов» after the silent refetch.
**Why human:** The original blocker was a live-only PostgREST embed failure; the offline regression simulates the PGRST201 rejection and the executor's live read probe was not re-run independently by the verifier.

#### 2. Long title + ready CTA layout (14-03 backstop)

**Test:** Open Admin Digest with a long draft title; confirm the draft badge and «Сделать ready» stay usable in the meta flex wrap.
**Expected:** Title wraps with `break-words`; badge and CTA remain clickable without overflow clipping.
**Why human:** Backstop must-have — layout usability; UAT test 1 exercised the row but recorded the (now-fixed) backend 503, not the layout.

### Gaps Summary

No goal-blocking gaps. All four UAT gaps are closed in code and regression-locked:

- **G-14-1 / G-14-4** — the `_fetch_one` embed now names the `from_material_id` FK (`material_relations!material_relations_from_material_id_fkey(to_material_id)`), removing the PGRST201 → `PersistenceError` → HTTP 503 path on the promote/read routes; an offline PGRST201-rejecting regression locks both `get()` and `get_by_slug()` and the embed shape.
- **G-14-2** — the batch promote CTA, its `promoteApprovedDrafts` handler/import, and the «Уберите черновики…» footer hint are removed; `sendHint` was reordered to a coherent neutral lock and the D-85 gate (`sendUnlocked` requires `approvedDrafts.length === 0`) is intact; locked by Playwright + a node source-shape assertion.
- **G-14-3** — a global `@layer base { button:not(:disabled) { cursor: pointer } }` rule restores the pointer affordance; locked by a computed-cursor Playwright assertion covering the audited controls and guarding disabled buttons.

Overall status is `human_needed` for two non-blocking human items: the live per-row promote re-check (the blocker was live-only) and the 14-03 long-title layout backstop. The remaining review warnings from `14-REVIEW.md` (WR-01 narrow non-string-label honesty edge; WR-02 `response.json()` parse-failure guard) are quality concerns, not gaps.

---

_Verified: 2026-10-03T18:55:00Z_
_Verifier: Claude (gsd-verifier)_
