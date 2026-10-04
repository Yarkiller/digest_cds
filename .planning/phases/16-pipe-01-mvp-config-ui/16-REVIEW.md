---
phase: 16-pipe-01-mvp-config-ui
reviewed: 2026-10-04T11:55:00Z
depth: standard
files_reviewed: 26
files_reviewed_list:
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
  - web/src/App.jsx
  - web/src/components/AppShell.jsx
  - web/src/main.jsx
  - web/src/pages/AdminPipelineConfigPage.jsx
  - web/src/services/pipelineConfigApi.js
findings:
  critical: 0
  warning: 5
  info: 4
  total: 9
status: issues_found
---

# Phase 16: Code Review Report

**Reviewed:** 2026-10-04T11:55:00Z
**Depth:** standard
**Files Reviewed:** 26
**Status:** issues_found

## Summary

Reviewed the PIPE-01 MVP config surface end-to-end: the port/use-case/domain layers,
the strict PyYAML+Pydantic validator adapter, the FastAPI read/write routes, the RLS
singleton Supabase adapter + migration 011, and the React admin page + service module.

The core architecture holds up. Dependencies point inward (no `yaml`/`pydantic`/Supabase
import in `domain/` or `use_cases/`); the adapter maps SDK/parse failures at the boundary;
the validator runs before `repo.save` so a reject writes nothing; the reject payload is a
top-level `{"errors":[...]}` 400; the DTO exposes exactly `{yaml, updated_at}`; the SPA
reaches storage only through `pipelineConfigApi.js`; and no execution control renders.
RLS is enabled with no permissive policy and the table is only touched by the service_role
client. I found no Critical/blocking defect.

The remaining findings are robustness and honesty issues: an undeclared direct `pydantic`
dependency, an incomplete exception boundary in the parser (deep nesting → 500 instead of a
structured 400), an overstated DoS comment around the length cap, and two real
unsaved-changes gaps in the editor. No source files were modified.

## Narrative Findings (AI reviewer)

### Critical Issues

None. No authentication bypass, injection, data-corruption, or write-on-reject path was
found. (`PUT` validates through `PipelineConfigValidator` before `repo.save` at
`application/use_cases/pipeline_config.py:32-33`, and the reject branch at
`interface/http/routes/admin.py:579-586` returns before any repository call.)

### Warnings

#### WR-01: `pydantic` imported directly but not declared as a dependency

**File:** `backend/pyproject.toml:7-14`, `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py:21`
**Issue:** The validator does `from pydantic import BaseModel, ConfigDict, Field, ValidationError`
and this phase correctly added `pyyaml==6.0.3` to `[project].dependencies`, but `pydantic`
was **not** added even though it is now a direct runtime import. It only resolves today as a
transitive dependency of `fastapi`. A future FastAPI major, a stricter resolver, or a
`uv lock` change can silently drop it and break `import backend` at runtime. Direct imports
must be declared as direct dependencies.
**Fix:**
```toml
dependencies = [
    ...
    "pydantic==2.11.7",   # pin to the version fastapi 0.141.1 resolves
    "pyyaml==6.0.3",
    ...
]
```

#### WR-02: Validator only catches `MarkedYAMLError`; deep documents escape as 500

**File:** `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py:87-107`
**Issue:** The only exception boundary around `yaml.load` is `except yaml.MarkedYAMLError`.
Deeply nested flow collections (e.g. ~2–5k nested `[` characters, trivially under the 20k
cap) drive PyYAML's recursive-descent parser into a Python `RecursionError`, which is **not**
a `MarkedYAMLError`. It propagates past the adapter and surfaces as an unhandled 500 rather
than a structured 400 `{"errors":[...]}`. The same is true for a bare `yaml.YAMLError`
raised without marks. The route only maps `PipelineConfigValidationError`, so the client sees
an opaque server error instead of the contract this phase promises.
**Fix:**
```python
        try:
            data = yaml.load(yaml_text, Loader=_StrictSafeLoader)
        except yaml.MarkedYAMLError as exc:
            ...
        except (yaml.YAMLError, RecursionError) as exc:
            raise PipelineConfigValidationError(
                (PipelineConfigError(path="", message=str(exc) or "Некорректный YAML"),)
            ) from exc
```
(Consider also lowering the effective nesting bound via a catch-all at the route boundary so
the surface can never emit a 500 for user-supplied text.)

#### WR-03: Length cap does not mitigate YAML alias expansion as the comment claims

**File:** `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py:26-28, 87-94`
**Issue:** The comment at line 26 states the 20 000-char cap covers "T-16-07: YAML alias /
oversized document DoS". A character cap does **not** bound anchor/alias expansion — the
classic "billion laughs" payload expands to gigabytes from a few hundred bytes, well inside
20k chars, and `SafeLoader` still expands aliases (SafeLoader only restricts *types*, not
expansion). There is also no request-body size limit on the PUT route, so the body is fully
read before the cap is even evaluated. The comment overstates the guarantee and may mislead
future maintainers into believing the surface is bounded.
**Fix:** Either reject aliases outright in `_StrictSafeLoader` (e.g. override `compose_node`
to raise on any anchor/alias), or lower the cap plus add an explicit alias-count limit, and
correct the comment so it does not claim alias-DoS protection the cap cannot provide.

#### WR-04: `window.confirm` inside `beforeunload` is unreliable

**File:** `web/src/pages/AdminPipelineConfigPage.jsx:110-120`
**Issue:** The unsaved-changes guard calls `window.confirm(UNSAVED_LEAVE_CONFIRM)`
**inside** the `beforeunload` handler. Modal dialogs are suppressed/ignored by browsers
during `beforeunload`; the platform-native prompt is driven by setting `event.returnValue`,
not by a scripted `confirm()`. In real browsers the custom prompt is a no-op (or a
double-prompt), so the guard's behavior is inconsistent, and the Playwright suite currently
only passes because it dispatches a synthetic event and stubs the dialog. This couples the
production code to a test-only interaction.
**Fix:** Drop `window.confirm` from the unload handler; the standard guard is:
```js
function onBeforeUnload(event) {
  event.preventDefault()
  event.returnValue = ''
}
```

#### WR-05: Unsaved edits are lost on in-app (SPA) navigation

**File:** `web/src/pages/AdminPipelineConfigPage.jsx:107-121`, `web/src/components/AppShell.jsx:64-96`
**Issue:** The only dirty guard is the `beforeunload` listener, which fires on tab
close/reload. Clicking any shell `NavLink` (`/`, `/archive`, `/admin/digest`, …) performs a
client-side route change that unmounts `AdminPipelineConfigPage` without firing
`beforeunload`, so the edited YAML is discarded silently. For an editor whose status copy
explicitly promises "Есть несохранённые изменения. Уйти без сохранения?", losing the draft
on every nav click is a real bug.
**Fix:** Add a router-level guard (e.g. `useBlocker` from `react-router-dom` v6 data/router
APIs) around the dirty state, prompting with the same `UNSAVED_LEAVE_CONFIRM` before allowing
in-app navigation, in addition to the unload guard.

### Info

#### IN-01: Playwright mock-control harness is exposed in every build

**File:** `web/src/main.jsx:63-68`
**Issue:** `window.__DIGEST_PIPELINE_CONFIG_HARNESS__` (and the other `__DIGEST_*` harnesses)
is assigned unconditionally on `window`, including production bundles. The handlers only take
effect while `isMocksEnabled()` is true, so this is low risk, but it still publishes mutation
controls (`armRejectNextSave`, `armFailNextSave`, …) to any script on the page.
**Fix:** Gate the harness assignment behind `import.meta.env.DEV || isMocksEnabled()` so
production bundles do not expose test-only globals.

#### IN-02: Duplicate imports in `test_live_container_wiring.py`

**File:** `tests/unit/test_live_container_wiring.py:11-19`
**Issue:** `InMemoryPingRecorder` and `InMemoryProfileRepository` are imported twice — once on
line 13 and again in the multi-name block on lines 11-19. Harmless but noisy and will trip
linters (F811).
**Fix:** Delete line 13 and keep the single consolidated import block.

#### IN-03: Mocks default to ON, so the new service silently no-ops without `VITE_USE_MOCKS=false`

**File:** `web/src/services/pipelineConfigApi.js:15,51,149-165,203-228`, `web/src/services/authEnv.js:7-11`
**Issue:** `isMocksEnabled()` returns `true` when `VITE_USE_MOCKS` is unset/empty, so a build
that forgets `VITE_USE_MOCKS=false` makes `savePipelineConfig` write only to
`sessionStorage` — the admin sees "Сохранено", nothing reaches Supabase, and no error is
raised. This default is inherited from D-09 (offline Playwright) and is broader than this
phase, but the pipeline surface is exactly where silent non-persistence is most damaging.
**Fix:** Ensure the production build/pipeline always sets `VITE_USE_MOCKS=false` (build-time
assert or fail-fast), and consider surfacing a visible "mock mode" banner when it is on.

#### IN-04: Migration relies solely on RLS; consider revoking default grants

**File:** `supabase-integration/migrations/011_phase16_pipeline_config.sql:14`
**Issue:** The table relies entirely on `enable row level security` (no policy) for
deny-by-default. That is correct for the current RLS-on state, but Supabase grants default
table privileges to `anon`/`authenticated`; if RLS is ever disabled or a policy is later added
accidentally, the grants become live. Defense-in-depth would revoke them explicitly.
**Fix:**
```sql
revoke all on public.pipeline_config from anon, authenticated;
```

---

_Reviewed: 2026-10-04T11:55:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
