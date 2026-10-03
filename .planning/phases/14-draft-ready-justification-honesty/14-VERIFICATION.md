---
phase: 14-draft-ready-justification-honesty
verified: 2026-10-04T00:20:00Z
status: human_needed
score: 22/24 must-haves verified
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
  - data-collection/src/data_collection/dto/_body.py
  - data-collection/src/data_collection/dto/article_draft.py
  - supabase-integration/src/supabase_integration/material_repository.py
  - tests/admin.spec.js
  - tests/unit/test_admin_mark_ready.js
  - tests/unit/test_article_draft_body_audience.py
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
covered_digest: "v2:sha256:650f9aef2368fa5fd603c6ef48a4dcd8cb3d0dca13846979f8a9e504cae7e065"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 19/20
  reason: "GSD #4682 stale re-verification — commit 9875a5c changed covered sources (healed the live promote WRITE path in SupabaseMaterialRepository.save + audience-leak normalisation) after the prior verifier ran, so the previous covered_digest no longer matched."
  gaps_closed:
    - "G-14-1 / G-14-4: read path — material_relations embed disambiguated by FK hint (plan 14-06)"
    - "G-14-1 / G-14-4: write path — save() now UPDATEs domain-owned columns by id instead of full-row upsert (commit 9875a5c)"
    - "G-14-2: batch promote CTA + «Уберите черновики…» hint removed; sendHint coherent; per-row + D-85 gate intact (plan 14-07)"
    - "G-14-3: global pointer-cursor base rule + computed-cursor Playwright lock (plan 14-08)"
  gaps_remaining: []
  regressions: []
  superseded:
    - "Prior truth: batch partial promote optimistic UI (14-03) — FE batch affordance removed by operator override (14-07); backend batch path retained and HTTP-covered"
    - "Prior truth: batch stale-refetch no-clobber reconcile (14-04 must_have #4) — no FE batch caller remains"
    - "Prior truth: quantified batch CTA «Сделать ready все одобренные черновики (N)» (14-05) — control removed by 14-07"
    - "Prior truth: sticky-footer batch-CTA geometry backstop (14-03) — batch CTA removed"
human_verification:
  - test: "Live per-row promote on real Supabase data (VITE_USE_MOCKS=false): approve a draft with a non-empty body, then click per-row «Сделать ready»"
    expected: "POST /admin/materials/{id}/ready returns 200 (not 503) and the row badge flips to «готов»; re-promote is a 200 no-op (idempotent) and published_at is untouched"
    why_human: "The G-14-1 blocker was live-only (PGRST201 read + 428C9/23502 write on the live schema). Both failure modes are now simulated offline by fakes, but the exact FK hint name is not locked by the regression (WR-03) and the verifier has no independent live network access; the executor's live probe (materials 10/11/12 draft→ready persisted) is narrative, not independently reproducible here"
  - test: "Long-title layout backstop (14-03): open Admin Digest with a long draft title and hover/click the per-row control"
    expected: "Title wraps with break-words; the draft badge and «Сделать ready» stay usable in the meta flex wrap without overflow clipping"
    why_human: "verification: backstop — a present break-words/flex-wrap cannot be proven usable by unit/presence checks; UAT recorded the (now-fixed) backend 503 on this row, not the layout"
  - test: "Long factor caption / empty justification wrap backstop (14-03): render a row with a long populated factor caption and a row with the exact empty sentence"
    expected: "Both wrap with break-words inside max-w-[12rem] without breaking the shortlist row grid"
    why_human: "verification: backstop — layout usability is not a programmatic assertion"
---

# Phase 14: Draft→ready & justification honesty Verification Report

**Phase Goal:** Admin can unblock send without SQL and see honest shortlist justification
**Verified:** 2026-10-04T00:20:00Z
**Status:** human_needed
**Re-verification:** Yes — stale re-verification (GSD #4682) after commit `9875a5c` changed covered sources. All four prior gaps (G-14-1/2/3/4) remain closed; the write-path fix is now independently re-verified from current code.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | SC1 / ADUX-05: Admin can set a material `draft` → `ready` in the admin UI without a direct SQL workaround | ✓ VERIFIED | `AdminDigestPage` `admin-mark-ready` → `adminApi.markReady` → `POST /admin/materials/{id}/ready`; Playwright `per-row Сделать ready promotes draft and clears draft hint (ADUX-05)` PASS |
| 2 | SC2 / ADUX-05: after promotion the D-85 send gate no longer blocks that material solely for still being draft | ✓ VERIFIED | `test_admin_mark_ready_promotes_draft_and_clears_send_gate` green; Playwright asserts the draft hint clears after promote |
| 3 | SC3 / ADUX-06: shortlist «Обоснование» shows populated `score_factors` or an explicit empty state — never a silent fake | ✓ VERIFIED | `factorText` returns the exact D-15 empty string for <2 labels, joins server labels only; `tests/unit/test_score_factors.py` named 0/1/2+/whitespace matrix green; Playwright asserts the exact string |
| 4 | D-06: status-only promote leaves `published_at` unchanged and never routes through `publish_material` / `Material.as_ready` | ✓ VERIFIED | `Material.with_ready_status` (`material.py:47-53`) uses `replace(status=READY, updated_at=now)` with no `assert_publishable`; `mark_material_ready.py` imports no publish/index path |
| 5 | Live promote **write path** persists draft→ready on the live superset schema (post-`9875a5c`) | ✓ VERIFIED | `SupabaseMaterialRepository.save` now `.update(payload).eq("id", ...)` (domain-owned columns only), guards empty `data`; `test_save_updates_owned_columns_by_id_instead_of_full_row_upsert` / `test_save_preserves_unmodelled_provenance_columns_on_the_live_row` / `test_save_signals_when_no_row_matches` green (428C9/23502 fakes) |
| 6 | D-09 / D-10: already-ready promote is a 200 no-op; empty body still promotes; missing material → 404 `material_not_found` | ✓ VERIFIED | `test_admin_mark_ready_already_ready_is_noop`, `test_admin_mark_ready_missing_material_returns_404`, `test_mark_material_ready_empty_body_draft_sets_ready_leaves_published_at` green |
| 7 | D-08: batch `POST /admin/materials/ready` returns HTTP 200 order-preserving partial success; `extra=forbid`; empty ids → `results=[]` | ✓ VERIFIED | `test_admin_mark_ready_batch_partial_success_preserves_order` / `_empty_ids_returns_empty_results` / `_unknown_field_returns_422` green (backend contract retained but unhooked from FE per 14-07) |
| 8 | D-02: Approve on a draft leaves `material_status` draft — approve ≠ ready | ✓ VERIFIED | `test_admin_decision_approve_returns_updated_shortlist_with_status` asserts `material_status == "draft"`; Playwright `Approve does not auto-ready draft (D-02)` PASS |
| 9 | D-01: per-row «Сделать ready» sits next to the draft badge and hides once ready | ✓ VERIFIED | `admin-mark-ready` testid in the row meta; Playwright per-row + stale tests assert it disappears after promote |
| 10 | D-05: after promote optimistic ready + silent refetch; on failure a toast and the badge stays draft — no fake ready | ✓ VERIFIED | Optimistic `setItems` + rollback-on-failure in `promoteReady`; reconciled refetch; Playwright per-row test PASS |
| 11 | G-14-2 (14-04): a still-draft refetch never silently reverts a promoted row | ✓ VERIFIED | Playwright `stale still-draft refetch does not revert a promoted row (G-14-2)` PASS; `__DIGEST_ADMIN_STALE_READY__` harness honoured by the `markReady` mock |
| 12 | G-14-2 (14-04): live `markReady` POSTs `/admin/materials/{id}/ready` and treats `MarkReadyResponse` as source of truth — no `fetchShortlist` coupling | ✓ VERIFIED | `adminApi.js` `markReady` body has no `fetchShortlist`; `return response.json()` (live) / `{material_id,status:'ready'}` (mock); node source-shape test green |
| 13 | G-14-2 (14-04): a still-draft refetch is reconciled best-effort via `preservePromotedReady` | ✓ VERIFIED | Pure helper node suite (still-draft→ready, identity when ready, multi-id, null/empty safe) green; `promoteReady` wraps `refreshed.items` |
| 14 | G-14-2 (14-04): a harness flag simulates a backend that acknowledges the POST without persisting | ✓ VERIFIED | `markReady` mock reads `stickyFlag('__DIGEST_ADMIN_STALE_READY__')` and skips `applyMockMarkReady`; `resetAdminHarness` clears it; Playwright stale test exercises it |
| 15 | 14-07: the footer offers no batch promote (CTA + handler + import gone) and the «Уберите черновики…» hint renders in no state; per-row control + D-85 gate intact | ✓ VERIFIED | No `admin-mark-ready-batch` / `promoteApprovedDrafts` / `markReadyBatch` in `AdminDigestPage.jsx`; `sendHint` branch order ends `… → «Отправка недоступна.»`; `sendUnlocked` still requires `approvedDrafts.length === 0`; Playwright `no batch promote CTA is rendered (G-14-2)` PASS; node source-shape lock green |
| 16 | G-14-2a (14-05): the approved-draft row reads as two disambiguated axes | ✓ VERIFIED | `materialStatusLabel` («черновик»/«готов») + `decisionCaption` («одобрен (в шортлист)»); Playwright D-02 case asserts both coexist |
| 17 | G-14-2b (14-05): the sticky send footer no longer re-lists approved-draft titles | ✓ VERIFIED | Footer renders only `admin-send-hint` + buttons (no `<ul>`); Playwright asserts footer `ul` count 0 |
| 18 | D-13…D-17 / ADUX-06: exact D-15 empty copy + populated server-only join + named `honest_factor_labels` 0/1/2+/whitespace matrix | ✓ VERIFIED | `factorText` exact string `Обоснование недоступно — скоринг не запускался`; `test_score_factors.py` named cases green; FE never fabricates labels |
| 19 | G-14-1 / G-14-4 (14-06): `_fetch_one` uses an FK-disambiguated `material_relations!material_relations_from_material_id_fkey(to_material_id)` embed so live `get()` / `get_by_slug()` return a `Material` (no PGRST201 → 503) | ✓ VERIFIED | `material_repository.py:151` emits the hinted embed; `material_tags` unhinted; offline PGRST201 regression green |
| 20 | G-14-1 (14-06): an offline regression fails on the bare embed and passes only after disambiguation | ✓ VERIFIED | `tests/unit/test_supabase_material_repository_embed.py` `test_get_returns_material_under_ambiguous_embed_rejection` / `test_get_by_slug_...` / `test_fetch_one_disambiguates_relations_embed_and_keeps_tags_unhinted` green (independently run) |
| 21 | G-14-3 (14-08): interactive admin controls show `cursor: pointer`, disabled buttons excluded, locked by a computed-cursor assertion | ✓ VERIFIED | `index.css` `@layer base { button:not(:disabled) { cursor: pointer } }`; Playwright `interactive admin controls show a pointer cursor (G-14-3)` PASS (audited controls + disabled Send guard) |
| 22 | 14-07: the retained backend batch route + `mark_materials_ready` and the unhooked FE `markReadyBatch` client/mock remain available and tested | ✓ VERIFIED | Backend batch HTTP tests green; `markReadyBatch` export + `applyMockMarkReadyBatch` node-tested; no UI caller remains (intentional) |
| 23 | 14-03 backstop: long material titles still wrap with usable draft badge + «Сделать ready» | ⚠️ insufficient_spec (backstop) | `break-words` / flex wrap present; `verification: backstop` — no held-out visual proof. See Human Verification |
| 24 | 14-03 backstop: long factor captions and the empty justification sentence wrap with `break-words` inside `max-w-[12rem]` | ⚠️ insufficient_spec (backstop) | Caption carries `max-w-[12rem] break-words`; `verification: backstop` — no held-out visual proof. See Human Verification |

**Score:** 22/24 truths verified (0 present-behavior-unverified; 2 backstop abstentions → human)

### Superseded Must-Haves (operator override, plan 14-07)

| Prior truth | Disposition |
| ----------- | ----------- |
| Batch partial promote: ok ids ready, failed ids toast + stay draft (D-08, FE) | FE batch affordance removed; backend batch path retained but unhooked and HTTP-covered |
| Batch promote path applies the same no-clobber reconcile to its ok ids | No FE batch caller remains |
| Quantified batch CTA «Сделать ready все одобренные черновики (N)» (14-05) | Batch control removed |
| Sticky-footer batch-CTA geometry backstop (many titles) | Batch CTA removed |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `supabase-integration/src/supabase_integration/material_repository.py` | FK-disambiguated relations embed in `_fetch_one`; `save` updates owned columns by id | ✓ VERIFIED | Hinted embed at L151; `save` uses `.update(...).eq("id", ...)` with empty-data guard |
| `tests/unit/test_supabase_material_repository_embed.py` | Offline PGRST201 read regression + write-path (428C9/23502) regression | ✓ VERIFIED | 9 tests included in the 35-pass targeted run |
| `web/src/pages/AdminDigestPage.jsx` | Batch CTA/handler/import removed; coherent `sendHint`; per-row retained; reconciled refetch | ✓ VERIFIED | No batch testid/handler/import; D-85 gate intact; `preservePromotedReady` wired |
| `web/src/index.css` | Global `button:not(:disabled){cursor:pointer}` base rule | ✓ VERIFIED | Present at L35-41 |
| `tests/admin.spec.js` | Playwright per-row/stale/no-batch/pointer-cursor/D-02 locks | ✓ VERIFIED | 36 tests PASS |
| `tests/unit/test_admin_mark_ready.js` | node `--test` reconcile + batch-removal source-shape lock | ✓ VERIFIED | 10 pass / 0 fail |
| `web/src/services/adminApi.js` | `markReady` decoupled from refetch; stale harness flag; `markReadyBatch` retained | ✓ VERIFIED | No `fetchShortlist` in `markReady`; `return response.json()` |
| `web/src/services/adminReadyReconcile.js` | Pure `preservePromotedReady` | ✓ VERIFIED | Identity-preserving; node suite green |
| `web/src/services/adminReadyMock.js` | Pure mock helpers; material 104 empty `factor_labels` seed | ✓ VERIFIED | Node suite green |
| `backend/src/backend/domain/material.py` | `with_ready_status` status-only transition | ✓ VERIFIED | No publish gate; `published_at` untouched |
| `backend/src/backend/domain/shortlist.py` | `honest_factor_labels` | ✓ VERIFIED | ≥2 rule; 0/1/2+/whitespace matrix green |
| `backend/src/backend/application/use_cases/mark_material_ready.py` | single + batch helpers | ✓ VERIFIED | status-only; per-id errors |
| `backend/src/backend/interface/http/routes/admin.py` | ready routes | ✓ VERIFIED | `require_admin`; batch before `{id}`; `extra=forbid` |
| `backend/src/backend/tests_support/in_memory.py` | shortlist status overlay | ✓ VERIFIED | `attach_materials` / `_overlay_batch` overlays `material_status` |
| `data-collection/src/data_collection/dto/_body.py` + `article_draft.py` | Normalise leaked `## Аудитория` prompt scaffolding out of `body_markdown` | ✓ VERIFIED | `test_article_draft_body_audience.py` (JSON / echoed-prompt / later-section / prose / idempotency) green |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `AdminDigestPage` «Сделать ready» | `POST /admin/materials/{id}/ready` | `markReady` (source of truth) → optimistic → reconciled refetch | ✓ WIRED | Playwright stale + per-row proof green |
| `SupabaseMaterialRepository.save` | PostgREST `materials` UPDATE | `.update(domain-owned payload).eq("id", material.id)` | ✓ WIRED | Offline 428C9/23502 regression green |
| `SupabaseMaterialRepository._fetch_one` | PostgREST `materials` embed | `material_relations!<fk>(to_material_id)` | ✓ WIRED | Offline PGRST201 regression green |
| native `<button>` (admin) | `index.css` `@layer base` | `button:not(:disabled){cursor:pointer}` | ✓ WIRED | Computed-cursor Playwright green |
| approved draft | `admin-send-footer` | `sendHint` neutral lock; no batch CTA; `sendUnlocked` D-85 | ✓ WIRED | Playwright D-85 + no-batch tests green |
| `factor_labels[]` | `factorText` caption | BE `honest_factor_labels` → shortlist DTO | ✓ WIRED | No fabricated defaults (see WR-01 edge) |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Admin shortlist badge | `item.material_status` | GET shortlist / materials join (live) or mock overlay | Yes | ✓ FLOWING |
| Ready promote (write) | `materials.status` | `mark_material_ready` → `SupabaseMaterialRepository.save` UPDATE by id | Yes | ✓ FLOWING |
| Post-promote reconcile | `refreshed.items` → `preservePromotedReady` | `fetchShortlist()` refetch wrapped before `applyBatch` | Yes | ✓ FLOWING |
| Обоснование caption | `item.factor_labels` | BE `honest_factor_labels` → shortlist DTO | Yes when ≥2 string labels; else D-15 empty | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full backend suite | `uv run pytest -q` | 684 passed in 8.04s | ✓ PASS |
| Embed read/write + ready/score/decision/audience units | `uv run pytest tests/unit/test_supabase_material_repository_embed.py tests/unit/test_mark_material_ready.py tests/unit/test_score_factors.py tests/unit/test_set_shortlist_decision.py tests/unit/test_article_draft_body_audience.py -q` | 35 passed | ✓ PASS |
| Admin HTTP ready + draft/approve | `uv run pytest tests/unit/test_http_admin.py -k "ready or approve or draft" -q` | 12 passed, 19 deselected | ✓ PASS |
| FE reconcile + batch-removal source lock | `node --test tests/unit/test_admin_mark_ready.js` | 10 pass / 0 fail | ✓ PASS |
| Admin Playwright (full file incl. G-14-2/G-14-3/D-02) | `npx playwright test tests/admin.spec.js` | 36 passed (1.6m) | ✓ PASS |
| `honest_factor_labels` non-string edge | `uv run python -c "from backend.domain.shortlist import honest_factor_labels as h; print(h({'factors':[{'label':None},{'label':None}]}))"` | `['None', 'None']` — see WR-01 | ✗ (advisory) |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| ADUX-05 | 14-01…14-08 | Admin sets material `draft`→`ready` in UI so send is not blocked by D-85 without SQL | ✓ SATISFIED | API + FE + unit/HTTP/Playwright (incl. stale-refetch lock + read/write heal) |
| ADUX-06 | 14-03 | Honest «Обоснование» — populated or explicit empty, no silent fake | ✓ SATISFIED | D-15 FE copy + `honest_factor_labels` matrix + Playwright exact assert (WR-01 non-string edge noted) |

No orphaned Phase 14 requirement IDs beyond ADUX-05 / ADUX-06 (REQUIREMENTS.md maps both to Phase 14; traceability marks both Complete).

### Prohibitions

| Statement | Verdict | Evidence |
| --------- | ------- | -------- |
| MUST NOT call `publish_material` / `as_ready` / `assert_publishable` / indexing on admin promote | ✓ held | `with_ready_status` + `mark_material_ready.py` grep clean |
| MUST NOT auto-ready on Approve / `set_shortlist_decision` | ✓ held | `test_admin_decision_approve_returns_updated_shortlist_with_status` + Playwright D-02 |
| MUST NOT implement batch via a FE-loop of single ready | ✓ held | `markReadyBatch` body never calls `markReady` (node test); FE no longer calls the batch path |
| MUST NOT return HTTP 207 / abort batch on missing id | ✓ held | HTTP 200 + per-id `material_not_found` |
| MUST NOT fabricate FE factor labels | ✓ held | `factorText` joins server labels only |
| MUST NOT add `score_factors` writers / PIPE UI this phase | ✓ held | No writers/UI added |
| MUST NOT couple Approve toolbar to `markReady` | ✓ held | `applyDecision` separate from `promoteReady` |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `backend/src/backend/domain/shortlist.py` | 23-27 | `str(f.get("label", ""))` coerces any non-string label — `honest_factor_labels({'factors':[{'label':None},{'label':None}]})` → `['None','None']` (WR-01) | ⚠️ Warning | Latent honesty edge: a DB `score_factors` with `null`/numeric labels renders fabricated chips. Not reachable from current product paths (no `score_factors` writers this phase; seed uses strings). Declared 0/1/2+/whitespace matrix is green. Recommend Phase 16 fixing (accept only `str` labels + matrix cases) |
| `web/src/services/adminApi.js` | 390-395 | Live `markReady` treats an unparseable 2xx body as failure, so `promoteReady` can roll back a persisted promote (WR-02) | ℹ️ Info | Edge (proxy truncation / unexpected 204); `response_model=MarkReadyResponse` makes it unlikely. `G-14-2` main class (refetch clobber) is fixed |
| `tests/unit/test_supabase_material_repository_embed.py` | 243-245 | Regression asserts any `material_relations!<hint>(...)` but not the exact FK constraint name (WR-03) | ℹ️ Info | A typo'd hint could pass the test and re-open the live 503; the shipped literal is live-verified. Recommend asserting the exact literal |
| `web/src/services/adminApi.js` / `main.jsx` | 406-436 / 30,55 | `markReadyBatch` + `getMockMarkReadyBatchCalls` now have no UI caller (IN-01) | ℹ️ Info | Intentional retention of the D-08 backend/client contract; dead bundle weight only |
| phase-modified sources | — | No `TBD` / `FIXME` / `XXX` debt markers (grep over all covered sources) | — | None |

### Human Verification Required

#### 1. Live per-row promote (G-14-1 read + write re-check)

**Test:** On live Supabase data (`VITE_USE_MOCKS=false`), approve a draft material with a non-empty body, then click per-row «Сделать ready»; re-click on the now-ready row.
**Expected:** `POST /admin/materials/{id}/ready` returns 200 (not 503); the badge flips to «готов» after the silent refetch; re-promote is a 200 no-op; `published_at` stays null.
**Why human:** The original blocker was live-only (PGRST201 read + 428C9/23502 write). Both modes are now simulated offline, but the exact FK hint name is not test-locked (WR-03) and the verifier has no independent live network access.

#### 2. Long title + ready CTA layout (14-03 backstop)

**Test:** Open Admin Digest with a long draft title; confirm the draft badge and «Сделать ready» stay usable in the meta flex wrap.
**Expected:** Title wraps with `break-words`; badge and CTA remain clickable without overflow clipping.
**Why human:** Backstop must-have — layout usability cannot be proven by unit/presence checks.

#### 3. Long factor caption / empty justification wrap (14-03 backstop)

**Test:** Render a row with a long populated factor caption and a row with the exact empty sentence.
**Expected:** Both wrap with `break-words` inside `max-w-[12rem]` without breaking the shortlist row grid.
**Why human:** Backstop must-have — layout usability cannot be proven programmatically.

### Gaps Summary

No goal-blocking gaps. All four prior UAT gaps (G-14-1…G-14-4) are closed in code and regression-locked, and the stale-triggering write-path fix is independently re-verified from current code:

- **G-14-1 / G-14-4 (read):** `_fetch_one` names the `from_material_id` FK (`material_relations!material_relations_from_material_id_fkey(to_material_id)`), removing the PGRST201 → `PersistenceError` → HTTP 503 path; an offline PGRST201-rejecting regression locks `get()` / `get_by_slug()` and the embed shape.
- **G-14-1 / G-14-4 (write):** `save` no longer full-row upserts; it UPDATEs domain-owned columns by id, so the live identity (`428C9`) and migration-007 NOT NULL provenance (`23502`) rejections cannot recur; locked by three offline write-path regressions.
- **G-14-2:** the batch promote CTA, `promoteApprovedDrafts` handler/import, and the «Уберите черновики…» footer hint are removed; `sendHint` is coherent and the D-85 gate (`sendUnlocked` requires `approvedDrafts.length === 0`) is intact; locked by Playwright + a node source-shape assertion. The refetch never silently reverts a confirmed promote (`preservePromotedReady` + stale-refetch harness).
- **G-14-3:** a global `@layer base { button:not(:disabled) { cursor: pointer } }` rule restores the pointer affordance; locked by a computed-cursor Playwright assertion including a disabled-button guard.

Overall status is `human_needed` for three non-blocking human items: the live per-row promote re-check (the original blocker was live-only; the exact FK hint is not test-locked) and the two 14-03 layout backstops. The remaining review warnings (WR-01 non-string-label honesty edge; WR-02 parse-failure rollback; WR-03 hint-name not locked) are quality concerns carried as `open` in `14-REVIEW-DISPOSITION.md`, not goal-blocking gaps — though WR-01 is the one worth fixing in Phase 16, since it touches the phase's central honesty mechanism.

---

_Verified: 2026-10-04T00:20:00Z_
_Verifier: Claude (gsd-verifier)_
