---
phase: 16-pipe-01-mvp-config-ui
verified: 2026-10-04T12:12:00Z
status: human_needed
score: 42/49 must-haves verified
covered_files:
  - .planning/phases/16-pipe-01-mvp-config-ui/16-01-PLAN.md
  - .planning/phases/16-pipe-01-mvp-config-ui/16-01-SUMMARY.md
  - .planning/phases/16-pipe-01-mvp-config-ui/16-02-PLAN.md
  - .planning/phases/16-pipe-01-mvp-config-ui/16-02-SUMMARY.md
  - .planning/phases/16-pipe-01-mvp-config-ui/16-03-PLAN.md
  - .planning/phases/16-pipe-01-mvp-config-ui/16-03-SUMMARY.md
  - .planning/phases/16-pipe-01-mvp-config-ui/16-04-PLAN.md
  - .planning/phases/16-pipe-01-mvp-config-ui/16-04-SUMMARY.md
  - backend/pyproject.toml
  - backend/src/backend/application/ports/pipeline_config.py
  - backend/src/backend/application/use_cases/pipeline_config.py
  - backend/src/backend/composition/container.py
  - backend/src/backend/composition/live.py
  - backend/src/backend/domain/errors.py
  - backend/src/backend/domain/pipeline_config.py
  - backend/src/backend/infrastructure/yaml_pipeline_config_validator.py
  - backend/src/backend/interface/http/app.py
  - backend/src/backend/interface/http/routes/admin.py
  - backend/src/backend/tests_support/in_memory.py
  - supabase-integration/migrations/011_phase16_pipeline_config.sql
  - supabase-integration/src/supabase_integration/__init__.py
  - supabase-integration/src/supabase_integration/pipeline_config_repository.py
  - tests/admin.spec.js
  - tests/unit/test_cors.py
  - tests/unit/test_http_pipeline_config.py
  - tests/unit/test_live_container_wiring.py
  - tests/unit/test_phase16_migration_011.py
  - tests/unit/test_pipeline_config_validator.py
  - tests/unit/test_supabase_pipeline_config_repository_contract.py
  - uv.lock
  - web/src/App.jsx
  - web/src/components/AppShell.jsx
  - web/src/main.jsx
  - web/src/pages/AdminPipelineConfigPage.jsx
  - web/src/services/pipelineConfigApi.js
covered_digest: "v2:sha256:9f13afc54940f46fd02109f17f8db71b8c7086b09f593c0189f349e580449536"
behavior_unverified: 7
overrides_applied: 0
behavior_unverified_items:
  - truth: "Config longer than the viewport scrolls within the editor container; the page toolbar stays reachable at 1280px and narrow widths"
    test: "Open /admin/pipeline as admin, paste a config longer than the viewport, resize the window to 1280px and to a narrow width"
    expected: "The editor scrolls internally (min-h-[20rem]/max-h-[60vh]); the Save toolbar stays visible and reachable and never overlaps the editor"
    why_human: "Overflow/layout behavior is not asserted by any automated test; only the CSS classes are present"
  - truth: "A very long YAML body scrolls with horizontal scroll for long lines and never pushes the toolbar off-screen"
    test: "Paste a YAML document with very long lines and many lines"
    expected: "Vertical + horizontal scroll inside the editor; toolbar stays on-screen"
    why_human: "Visual overflow is not test-asserted; classes (overflow-auto, wrap=off) are present but unexercised"
  - truth: "The Save toolbar stays reachable and never overlaps the editor at 1280px and narrow widths"
    test: "Resize /admin/pipeline across 1280px and narrow widths while the editor holds content"
    expected: "Toolbar remains reachable, no overlap with editor"
    why_human: "Responsive layout needs visual confirmation"
  - truth: "The empty-state block and editor stay within the page at narrow widths; body copy wraps without horizontal overflow"
    test: "Open /admin/pipeline with no saved config at a narrow viewport"
    expected: "Empty-state copy wraps, no horizontal page overflow"
    why_human: "Responsive layout needs visual confirmation"
  - truth: "The nav item stays visible and usable when the app shell is narrow"
    test: "As admin, narrow the viewport and inspect the «Пайплайн» nav item"
    expected: "Nav item remains visible and usable"
    why_human: "Responsive chrome needs visual confirmation"
  - truth: "A long list of validation errors scrolls with the page and never overlaps or hides the editor's Save toolbar"
    test: "Trigger a reject with many structured errors"
    expected: "Error list scrolls with the page; toolbar not hidden"
    why_human: "Requires a large error payload and visual inspection"
  - truth: "Long server error messages wrap with break-words inside the panel without horizontal overflow"
    test: "Trigger a reject whose message is a long unbroken token"
    expected: "Message wraps inside the panel (break-words), no horizontal overflow"
    why_human: "Visual wrapping is not asserted by an automated test"
human_verification:
  - test: "Live persistence round-trip (PIPE-03 DoD): in live mode (VITE_USE_MOCKS=false against the shared VM), open /admin/pipeline as admin, save a valid YAML document, reload, and confirm the saved YAML is returned"
    expected: "The saved document is persisted to public.pipeline_config (id=1) and read back on a subsequent admin session; count becomes 1"
    why_human: "The remote shared-VM schema is applied (operator-recorded) but no automated test in this repo can perform a live save→read against it; local unit/Playwright runs use the in-memory fake / sessionStorage mock"
  - test: "Visual overflow/backstop checks on /admin/pipeline (7 items in behavior_unverified_items)"
    expected: "Editor scrolls internally, toolbar reachable, error panel wraps, nav usable at narrow widths"
    why_human: "Backstop (visual) truths with no automated assertion"
  - test: "Unsaved-changes guard in a real browser (WR-04/WR-05): edit the YAML, then (a) close/reload the tab and (b) click an in-app NavLink such as «Архив»"
    expected: "A leave-confirm is presented; Cancel keeps the edit. Note the code uses window.confirm inside beforeunload (unreliable in real browsers) and registers no router-level guard, so in-app SPA navigation currently discards the draft without a prompt"
    why_human: "WR-04/WR-05 are open review warnings; the Playwright test only dispatches a synthetic beforeunload event"
  - test: "Deep-nesting robustness (WR-02): PUT a config of ~3000 unclosed/closed nested flow brackets (under the 20k cap)"
    expected: "A structured 400 {errors:[...]} — but the live probe returned an unhandled RecursionError (would surface as HTTP 500), NOT a structured reject"
    why_human: "Confirmed by probe; decide whether to fix now or accept as a known robustness gap (no write occurs either way — no silent accept)"
---

# Phase 16: PIPE-01 MVP config UI Verification Report

**Phase Goal:** Admin can view, validate, and persist pipeline config without running the pipeline
**Verified:** 2026-10-04T12:12:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | **SC1** Admin can view and edit YAML pipeline config through an admin UI | ✓ VERIFIED | `AdminPipelineConfigPage.jsx` (raw monospace `<textarea data-testid=pipeline-config-editor>`), `admin/pipeline` route in `App.jsx:40`, «Пайплайн» nav in `AppShell.jsx:91`; Playwright happy path green |
| 2 | **SC2** Invalid config rejected before save with field-level/structured errors (no silent accept) | ✓ VERIFIED | Validator (strict SafeLoader + `extra=forbid`) → `PipelineConfigValidationError` → top-level `JSONResponse(400, {"errors":[…]})`; route calls repo 0 times on reject; unit+Playwright green (see WR-02 caveat) |
| 3 | **SC3** Validated config persists and is readable on subsequent sessions (storage behind a port; no deep Supabase coupling in UI) | ✓ VERIFIED | `SupabasePipelineConfigRepository` implements the `PipelineConfigRepository` port; wired only in `composition/live.py`; migration 011 applied on shared VM; boundary guard test green. Live round-trip → human |
| 4 | **SC4** No run/trigger/scheduler execution ships this phase | ✓ VERIFIED | No banned control strings; Playwright `pipeline config no execution controls render` green |
| 5 | 16-01: editor shows saved YAML on mount | ✓ VERIFIED | Playwright happy path; `fetchPipelineConfig()` on admin role effect |
| 6 | 16-01: save PUTs and GET returns saved value on reload | ✓ VERIFIED | Playwright `page.reload()` read-back; unit round-trip |
| 7 | 16-01: empty store → GET 200 `{yaml:'', updated_at:null}` | ✓ VERIFIED | `test_get_returns_empty_state_when_absent`; Playwright empty state |
| 8 | 16-01: load is page-level «Загрузка…» (aria-busy); editor not interactive until ready | ✓ VERIFIED | `AdminPipelineConfigPage.jsx` loading branch (`aria-busy`, testid `pipeline-config-loading`); editor only rendered after `ready` |
| 9 | 16-01: save disables Save, sets aria-busy, «Сохранение…» → «Сохранено» | ✓ VERIFIED | `saving` state disables both controls, `aria-busy={saving}`, status caption; Playwright asserts «Сохранено» |
| 10 | 16-01: /admin/pipeline renders only for role=admin | ✓ VERIFIED | Role gate in page; Playwright nav admin/employee cases |
| 11 | 16-01: GET/PUT require require_admin (401 unauth / 403 employee) | ✓ VERIFIED | `test_get_put_require_admin_unauth_401_and_employee_403` |
| 12 | 16-01: read DTO exposes exactly {yaml, updated_at}, no secret key | ✓ VERIFIED | `test_dto_exposes_only_yaml_and_updated_at_keys` |
| 13 | 16-01 backstop: raw YAML textarea, no structured field builder | ✓ VERIFIED | Code is a `<textarea>`; no builder component |
| 14 | 16-02: invalid YAML syntax → 400 top-level errors, nothing persisted | ✓ VERIFIED | `test_put_invalid_yaml_returns_400_top_level_errors_and_writes_nothing` |
| 15 | 16-02: duplicate top-level keys rejected (no last-wins) | ✓ VERIFIED | `_StrictSafeLoader.construct_mapping`; `test_duplicate_top_level_key_is_rejected_not_last_wins` |
| 16 | 16-02: unknown keys rejected via `extra="forbid"` | ✓ VERIFIED | `test_unknown_key_is_rejected_by_extra_forbid` |
| 17 | 16-02: reject carries no write (repo called 0 times) | ✓ VERIFIED | `save_count == 0` asserted in route tests |
| 18 | 16-02: reject payload is top-level `{"errors":[...]}`, never nested under detail | ✓ VERIFIED | `test_put_invalid_error_rows_are_verbatim_and_top_level` (`"detail" not in body`) |
| 19 | 16-02: schema exposes exactly {template, roles, language, max_chars} | ✓ VERIFIED | `test_schema_exposes_only_documented_non_secret_keys` |
| 20 | 16-02: yaml/pydantic imported only in infrastructure; domain/use_cases clean | ✓ VERIFIED | `yaml`/`pydantic` only in `yaml_pipeline_config_validator.py`; domain/use-case modules import neither |
| 21 | 16-02: AppContainer declares fields (None defaults) + build_in_memory_container wires real validator | ✓ VERIFIED | `test_build_in_memory_container_wires_real_validator_and_repo`; `test_app_container_still_constructs_without_pipeline_kwargs` |
| 22 | 16-02 backstop: re-saving same YAML yields one singleton row | ✓ VERIFIED | `save()` upserts fixed `id=1`; contract test asserts upsert payload |
| 23 | 16-02 backstop: concurrent saves last-write-wins, no version guard | ✓ VERIFIED | Upsert with no optimistic guard (as decided D-09/D-11) |
| 24 | 16-03: adapter get/save at id=1; None when absent | ✓ VERIFIED | `test_supabase_pipeline_config_repository_contract.py` |
| 25 | 16-03: SDK failures → PersistenceError; existing PersistenceError re-raised unchanged | ✓ VERIFIED | Contract test (error-mapping cases) |
| 26 | 16-03: build_live_container wires Supabase adapter + real validator; no client outside composition | ✓ VERIFIED | `live.py:61-62`; `test_live_container_wiring.py -k pipeline` |
| 27 | 16-03: migration 011 singleton + RLS + no policy + no wipe | ✓ VERIFIED | `test_phase16_migration_011.py`; file inspected |
| 28 | 16-03: over-cap PUT → 400 {errors}, write count stays 0 | ✓ VERIFIED | Over-cap validator test; route maps `PipelineConfigValidationError` → 400 |
| 29 | 16-03: CORS advertises PUT | ✓ VERIFIED | `test_cors.py#test_put_method_is_advertised_in_cors_preflight`; `app.py` allow_methods includes PUT |
| 30 | 16-03: migration applied on shared VM before DoD claim | ✓ VERIFIED | Runbook §4h `Applied (2026-10-04)`; operator confirmed; read-only PostgREST probe → `[]` |
| 31 | 16-03 backstop: absent row is a valid empty state, not an error | ✓ VERIFIED | Empty-state DTO test + Playwright |
| 32 | 16-04: empty state locked copy + placeholder + Save disabled | ✓ VERIFIED | Playwright `pipeline config empty state…` |
| 33 | 16-04: dirty gating enables Save/reset; «Изменений нет» while clean | ✓ VERIFIED | Playwright `pipeline config dirty gating…` |
| 34 | 16-04: reset/unsaved confirm copy exact | ✓ VERIFIED | Playwright confirm cases; constants in page |
| 35 | 16-04: load failure copy + retry recovers | ✓ VERIFIED | Playwright `pipeline config load error…` |
| 36 | 16-04: each structured error row verbatim + generic fallback | ✓ VERIFIED | Playwright validation cases |
| 37 | 16-04: save failure ErrorPanel + retry can succeed | ✓ VERIFIED | Playwright `pipeline config save failure…` |
| 38 | 16-04: aria-invalid on reject; stale errors cleared on edit | ✓ VERIFIED | Playwright `…clears stale errors on edit` |
| 39 | 16-04: rejected save keeps document editable + dirty, never auto-reverted | ✓ VERIFIED | Playwright validation case asserts value unchanged + Save enabled |
| 40 | 16-04: page + nav render only for admin | ✓ VERIFIED | Playwright nav admin/employee cases |
| 41 | 16-04: no banned execution control strings render | ✓ VERIFIED | Playwright `pipeline config no execution controls render` |
| 42 | 16-04: page imports no supabase; reaches storage only via pipelineConfigApi.js | ✓ VERIFIED | `test_pipeline_page_reaches_storage_only_through_service_no_supabase` |
| 43 | 16-04 backstop: long config scrolls inside editor; toolbar reachable | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Classes present; no automated visual test — see Human Verification |
| 44 | 16-04 backstop: very long YAML scrolls; toolbar never pushed off-screen | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Classes present; unexercised |
| 45 | 16-04 backstop: Save toolbar reachable, no overlap at 1280px/narrow | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Responsive layout unasserted |
| 46 | 16-04 backstop: empty-state block + editor within page at narrow widths | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Responsive layout unasserted |
| 47 | 16-04 backstop: nav item visible/usable when shell narrow | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Responsive chrome unasserted |
| 48 | 16-04 backstop: long error list scrolls, never hides toolbar | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Needs large payload + visual check |
| 49 | 16-04 backstop: long server messages wrap with break-words | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `break-words` present; unexercised |

**Score:** 42/49 must-haves verified (7 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `backend/src/backend/domain/pipeline_config.py` | `PipelineConfig` + `PipelineConfigError` dataclasses | ✓ VERIFIED | Frozen dataclasses; `to_dict()` omits line when None |
| `backend/src/backend/application/ports/pipeline_config.py` | Repository + Validator Protocols | ✓ VERIFIED | Both Protocols present |
| `backend/src/backend/application/use_cases/pipeline_config.py` | get/save use-cases, validate-before-persist | ✓ VERIFIED | `validator.validate()` before `repo.save()` |
| `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py` | strict SafeLoader + Pydantic validator | ✓ VERIFIED | Sole `yaml`/`pydantic` import site |
| `backend/src/backend/interface/http/routes/admin.py` | GET/PUT `/admin/pipeline/config` | ✓ VERIFIED | Thin routes, `require_admin`, 400 reject, 503 guards |
| `backend/src/backend/composition/container.py` | pipeline_config fields + in-memory wiring | ✓ VERIFIED | None-defaulted fields; wired fakes |
| `backend/src/backend/composition/live.py` | live adapter + validator wiring | ✓ VERIFIED | `SupabasePipelineConfigRepository(admin_client)` + `YamlPipelineConfigValidator()` |
| `web/src/services/pipelineConfigApi.js` | sole SPA transport boundary | ✓ VERIFIED | fetch/save + 400 INVALID_CONFIG mapping + harness arms |
| `web/src/pages/AdminPipelineConfigPage.jsx` | complete editor surface | ✓ VERIFIED | empty/dirty/reset/error panel/save-retry |
| `web/src/App.jsx` | `admin/pipeline` route | ✓ VERIFIED | Inside RequireAuth + AppShell |
| `web/src/components/AppShell.jsx` | admin-gated «Пайплайн» nav | ✓ VERIFIED | `appRole === 'admin'` |
| `web/src/main.jsx` | harness exposure | ✓ VERIFIED | `window.__DIGEST_PIPELINE_CONFIG_HARNESS__` |
| `supabase-integration/migrations/011_phase16_pipeline_config.sql` | singleton + RLS, no policy | ✓ VERIFIED | Inspected; contract test green |
| `supabase-integration/src/supabase_integration/pipeline_config_repository.py` | Supabase adapter | ✓ VERIFIED | get/save id=1, PersistenceError mapping |
| `supabase-integration/src/supabase_integration/__init__.py` | export | ✓ VERIFIED | Import + `__all__` entry |
| `docs/agents/local-platform-runbook.md` §4h | apply + verify | ✓ VERIFIED | Applied 2026-10-04 recorded |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `AdminPipelineConfigPage.jsx` | `pipelineConfigApi.js` | `fetchPipelineConfig`/`savePipelineConfig` | ✓ WIRED | Import present; boundary guard test green |
| `pipelineConfigApi.js` | `routes/admin.py` | GET/PUT `/admin/pipeline/config` Bearer | ✓ WIRED | URL only in service (guard test) |
| `routes/admin.py` | ports + use-case | `get_pipeline_config`/`save_pipeline_config` | ✓ WIRED | `save_pipeline_config` calls validator then repo |
| `use_cases/pipeline_config.py` | `yaml_pipeline_config_validator.py` | `validator.validate` before `repo.save` | ✓ WIRED | Zero writes on reject asserted |
| `yaml_pipeline_config_validator.py` | `domain/errors.py` | `PipelineConfigValidationError` | ✓ WIRED | Mapping at adapter boundary |
| `domain/errors.py` | `routes/admin.py` | 400 top-level `{"errors":[…]}` | ✓ WIRED | `JSONResponse(400, …)`, not `HTTPException` |
| `live.py` | `pipeline_config_repository.py` | `SupabasePipelineConfigRepository(admin_client)` | ✓ WIRED | Wiring test green |
| `AppShell.jsx` | `/admin/pipeline` | admin-gated NavLink | ✓ WIRED | Playwright nav cases |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `AdminPipelineConfigPage.jsx` | `yaml` | `fetchPipelineConfig()` → GET `/admin/pipeline/config` → `PipelineConfigRepository.get()` | Yes (live: Supabase adapter; mock: sessionStorage) | ✓ FLOWING |
| `AdminPipelineConfigPage.jsx` | save result | `savePipelineConfig()` → PUT → `save_pipeline_config` → validator → `repo.save()` | Yes | ✓ FLOWING |
| `routes/admin.py` GET | response DTO | `get_pipeline_config(repo)` | Yes | ✓ FLOWING |
| `routes/admin.py` PUT | response DTO | `save_pipeline_config(repo, validator, …)` | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Phase 16 backend unit/contract tests | `uv run pytest tests/unit/test_http_pipeline_config.py tests/unit/test_pipeline_config_validator.py tests/unit/test_phase16_migration_011.py tests/unit/test_supabase_pipeline_config_repository_contract.py tests/unit/test_live_container_wiring.py tests/unit/test_cors.py -q` | 47 passed | ✓ PASS |
| Full backend regression | `uv run pytest -q` | 757 passed | ✓ PASS |
| Playwright admin surface (incl. 13 pipeline cases) | `npx playwright test --project=web tests/admin.spec.js` | 50 passed | ✓ PASS |
| Deep-nesting rejection (WR-02 probe) | `YamlPipelineConfigValidator().validate('['*3000 + ']'*3000)` | `UNHANDLED RecursionError` | ✗ FAIL (edge) |
| No debt markers in phase files | `rg "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER" <phase files>` | no matches (exit 1) | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| PIPE-01 | 16-01, 16-04 | Admin can view and edit YAML pipeline config through an admin UI | ✓ SATISFIED | Page + route + editor; Playwright happy path, empty/dirty/reset/nav/no-execution |
| PIPE-02 | 16-02, 16-04 | Config validated before save; invalid rejected with field-level/structured errors (no silent accept) | ✓ SATISFIED | Strict validator → top-level 400 errors, zero writes; UI renders every error; see WR-02 caveat |
| PIPE-03 | 16-01, 16-03, 16-04 | Validated config persists and is readable on subsequent sessions (storage behind a port; no deep Supabase coupling in UI) | ✓ SATISFIED | Supabase adapter behind port, wired in composition; migration 011 applied; SPA boundary guard; live round-trip → human |

No orphaned requirements: REQUIREMENTS.md maps PIPE-01/02/03 to Phase 16 and all three are declared across 16-01…16-04.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER markers in phase files | — | Clean |

### Code Review Findings (advisory, non-blocking)

16-REVIEW.md recorded 0 critical / 5 warning / 4 info, all dispositioned `open` in 16-REVIEW-DISPOSITION.md. Weighted against the success criteria:

- **WR-01** pydantic imported directly but undeclared in `backend/pyproject.toml`. Resolves transitively via FastAPI today; a direct dep would harden `import backend`. Not a SC violation.
- **WR-02** validator only catches `MarkedYAMLError`; deeply nested flow collections raise an unhandled `RecursionError` (probe-confirmed) → HTTP 500 instead of a structured 400. No write occurs either way, so SC2's "no silent accept" holds; the "structured errors" clause is incomplete for this edge. Affects PIPE-02 robustness.
- **WR-03** the 20 000-char cap comment overstates alias-expansion DoS protection. Documentation/robustness, not a SC failure.
- **WR-04** `window.confirm` inside `beforeunload` is unreliable in real browsers. The Playwright test passes only via a synthetic event. Affects the unsaved-leave guard reliability.
- **WR-05** unsaved edits are lost on in-app SPA navigation (no router-level guard). The draft is discarded silently on NavLink clicks. Real UX gap, outside the four SCs.
- **IN-01…IN-04** harness exposure in prod bundles; duplicate test imports; mocks default ON (`VITE_USE_MOCKS` unset → silent mock no-op); RLS-only grants. Info-level.

### Human Verification Required

#### 1. Live persistence round-trip (PIPE-03 DoD)

**Test:** In live mode against the shared knowledge-db VM (`VITE_USE_MOCKS=false`), open `/admin/pipeline` as admin, save a valid YAML config, reload the page, and confirm the saved YAML reads back.
**Expected:** The document persists to `public.pipeline_config` (id=1) and is returned on a subsequent admin session; `select count(*)` becomes 1.
**Why human:** The schema apply is operator-recorded (runbook §4h, 2026-10-04) but no automated test can perform a live save→read against the shared VM; local runs use the in-memory fake / sessionStorage mock. Current live probe shows 0 rows (expected empty state).

#### 2. Visual overflow/backstop checks (7 items)

**Test:** On `/admin/pipeline`, with a long config and many/long validation errors, verify at 1280px and at a narrow width: editor scrolls internally, Save toolbar stays reachable and non-overlapping, error rows and long messages wrap (`break-words`), empty state fits, «Пайплайн» nav stays usable.
**Expected:** No toolbar occlusion, no horizontal page overflow.
**Why human:** Seven backstop (visual) truths in 16-04 have no automated assertion.

#### 3. Unsaved-changes guard in a real browser (WR-04 / WR-05)

**Test:** Edit the YAML, then (a) close/reload the tab and (b) click an in-app NavLink (e.g. «Архив»).
**Expected:** A leave-confirm is shown and Cancel preserves the draft. Note: the implementation uses `window.confirm` inside `beforeunload` (unreliable) and registers no router-level guard, so in-app navigation currently discards the draft without a prompt.
**Why human:** Open review warnings; Playwright only dispatches a synthetic beforeunload event.

#### 4. Deep-nesting robustness (WR-02)

**Test:** PUT a ~6000-char document of nested flow brackets (under the 20k cap).
**Expected per contract:** structured `400 {errors:[…]}`. **Observed:** unhandled `RecursionError` → HTTP 500 (probe-confirmed). No write occurs either way.
**Why human:** Decide whether to fix now (broaden the exception boundary) or accept as a known robustness gap.

### Gaps Summary

No phase-blocking gaps. All four roadmap success criteria are met by code present, wired, and exercised by automated tests. The storage adapter sits behind `PipelineConfigRepository`, migration 011 is applied, and the SPA has no Supabase coupling (guard-tested). The 7 behavior-unverified items are visual/overflow backstops that route to human verification, and the live multi-session round-trip is a human step. The open code-review warnings (WR-01…WR-05, IN-01…IN-04) are pre-dispositioned advisory and do not block phase completion; WR-02 (deep-nesting 500) and WR-04/WR-05 (unsaved-changes guard) merit human judgment but do not violate the stated success criteria.

---

_Verified: 2026-10-04T12:12:00Z_
_Verifier: Claude (gsd-verifier)_
