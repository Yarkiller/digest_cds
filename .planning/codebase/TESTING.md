# Testing Patterns

**Analysis Date:** 2026-09-19

## Test Framework

**Runner:**
- Unit: pytest `>=8.3.0` (root `pyproject.toml` dependency group `dev`)
  - Config: `[tool.pytest.ini_options]` in root `pyproject.toml`
  - `testpaths = ["tests/unit"]`, `pythonpath = ["."]`
- E2E / UI: Playwright `@playwright/test` `^1.62.1` (root `package.json`)
  - Config: `playwright.config.js`

**Assertion Library:**
- pytest built-in `assert` / `pytest.raises`
- Playwright `expect` from `@playwright/test`
- Pydantic `ValidationError` for DTO rejection cases

**Run Commands:**
```bash
npm test                      # All Playwright projects
npm run test:web              # Playwright project `web` only
npm run test:design           # Playwright project `design-frontend` only
npm run test:unit             # uv run pytest (tests/unit)
uv run pytest                 # Same unit suite
uv run pytest tests/unit/test_publish_and_index.py   # Single file
npx playwright test --project=web tests/web-app.spec.js
```

**Browser install (Playwright):**
```bash
npm run playwright:install    # scripts/ensure-playwright-browsers.cjs
```
Browsers cache under `.playwright-browsers` via `PLAYWRIGHT_BROWSERS_PATH` in `playwright.config.js`.

## Test File Organization

**Location:**
- Unit: separate tree `tests/unit/` (not co-located under `src/`)
- E2E: `tests/*.spec.js`
- Shared fakes: `backend/src/backend/tests_support/` (importable package, not under `tests/`)

**Naming:**
- Unit: `test_<subject>.py` — e.g. `test_search_knowledge.py`, `test_foundry_dtos.py`
- Functions: `test_<behavior>_...` describing outcome
- E2E: `<surface>.spec.js` matched by Playwright `testMatch`

**Structure:**
```
tests/
├── unit/
│   ├── test_publish_and_index.py
│   ├── test_search_knowledge.py
│   ├── test_composition_container.py
│   ├── test_foundry_dtos.py
│   ├── test_youtube_source_dto.py
│   ├── test_text_import_dto.py
│   └── test_schema_migration_contract.py
├── web-app.spec.js
└── design-frontend.spec.js
```

## Test Structure

**Suite Organization (pytest):**
```python
"""RED→GREEN: material publish gate and knowledge chunk indexing."""

from datetime import datetime, timezone
import pytest
from backend.domain.errors import MaterialValidationError
from backend.application.use_cases.publish_material import publish_material
from backend.tests_support.in_memory import InMemoryMaterialRepository


def _draft(**overrides: object) -> Material:
    # factory helper in the same module
    ...


def test_publish_material_rejects_empty_body() -> None:
    repo = InMemoryMaterialRepository([_draft(body_markdown="")])
    with pytest.raises(MaterialValidationError):
        publish_material(repo, material_id=1)
```

**Suite Organization (Playwright):**
```javascript
const { expect, test } = require("@playwright/test");

test.describe("web app main flows", () => {
  test("opens a material from the issue table of contents", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /новости ds для сва/i })).toBeVisible();
  });
});
```

**Patterns:**
- Module docstring states the intended behavior / TDD slice (`RED→GREEN: ...`)
- Prefer factories (`_draft`) over duplicated entity construction when multiple cases share a base
- Annotate test functions with `-> None`
- Playwright groups via `test.describe` by flow / UI states / edge cases / responsive
- Prefer role/label locators over CSS selectors; use `getByTestId` only for state hooks (`confirm-vote`, `kb-skeleton`)

## Mocking

**Framework:** No unittest.mock / Vitest mocks as the default pattern

**Patterns:**
```python
# In-memory Protocol fakes (preferred for ports)
from backend.tests_support.in_memory import (
    InMemoryMaterialRepository,
    InMemoryKnowledgeChunkRepository,
)

materials = InMemoryMaterialRepository([material])
chunks = InMemoryKnowledgeChunkRepository()

# Callable stubs for side effects
index_material_chunks(..., embed=lambda text: [0.02] * 1024)
```

```javascript
// Frontend API harness for E2E error paths (not Jest mocks)
import { armFailNextVoteSubmit, submitVote } from '../services/votingApi.js'
// Or arm via URL: /voting?simulateError=1 (VotingPage)
```

**What to Mock / Fake:**
- Repository ports → `InMemory*` in `backend/src/backend/tests_support/in_memory.py`
- Embedding / external compute → lambda or simple callable injected into use-case
- Vote API failure → service harness (`armFailNextVoteSubmit` / query param), not network stubs

**What NOT to Mock:**
- Domain entities and pure use-case logic — exercise real `Material`, `publish_material`, etc.
- Pydantic DTO validation — construct real models; assert `ValidationError`
- Accessibility-visible UI behavior in Playwright — assert real DOM roles/text
- Do not write “unit” tests that hit live Supabase/network without an explicit integration marker (none present yet)

## Fixtures and Factories

**Test Data:**
```python
def _draft(**overrides: object) -> Material:
    base = {
        "id": 1,
        "slug": "rag-systems",
        "title": "Building Production RAG Systems",
        # ... required Material fields ...
        "status": MaterialStatus.DRAFT,
    }
    base.update(overrides)
    return Material(**base)  # type: ignore[arg-type]
```

```python
# Inline entity construction when a single test needs a custom shape
material = Material(
    id=7,
    slug="pgvector",
    title="pgvector for Enterprise Search",
    ...
)
```

**Location:**
- Factories: co-located in the test module (`_draft` in `test_publish_and_index.py`)
- Shared fakes: `backend/src/backend/tests_support/in_memory.py`
- Frontend demo data: `web/src/data/mock.js` (consumed by app + E2E, not a pytest fixture)
- Contract fixture: SQL file path `supabase-integration/migrations/001_initial_schema.sql` read as text

## Coverage

**Requirements:** None enforced (no coverage tool / threshold in `pyproject.toml` or CI)

**View Coverage:**
```bash
# Not configured — if adding later, prefer:
# uv run pytest --cov=backend --cov=data_collection
```

**TDD policy (mandatory):** Red → Green → Refactor. No production code without a failing test first (see `.cursor/rules/tdd.mdc`, `AGENTS.md`). Exceptions only for configs/generated/prototypes with explicit agreement.

## Test Types

**Unit Tests:**
- Scope: domain entities, use-cases with in-memory ports, Pydantic DTO validation, composition root wiring, SQL migration contract
- Approach: real domain code + fakes; no HTTP server
- Files: `tests/unit/*.py`
- Run: `uv run pytest` / `npm run test:unit`

**Integration Tests:**
- Not detected as a separate suite
- When adding: mark explicitly, keep out of default `tests/unit` path, and do not call them “unit”

**E2E Tests:**
- Playwright against:
  - React app (`project: web`, baseURL `http://127.0.0.1:5174`) — `tests/web-app.spec.js`
  - Static design concept (`project: design-frontend`, baseURL `http://127.0.0.1:8765`) — `tests/design-frontend.spec.js`
- `webServer` entries start only for selected projects (`playwright.config.js`)
- Covers main flows, UI states (loading/success/error), empty/not-found recovery, responsive viewports
- Responsive evidence screenshots written under `docs/digest-cds/responsive-evidence/`

**Contract / Schema Tests:**
- `tests/unit/test_schema_migration_contract.py` asserts required tables, `vector(`, `tsvector`, and RLS enablement strings exist in the migration SQL

## Common Patterns

**Async Testing:**
```javascript
test("confirms a vote with loading then success state", async ({ page }) => {
  await page.goto("/voting");
  await page.getByRole("radio", { name: /RAG в корпоративной среде/i }).click();
  const confirm = page.getByTestId("confirm-vote");
  await confirm.click();
  await expect(confirm).toHaveAttribute("data-state", "loading");
  await expect(confirm).toHaveAttribute("data-state", "success");
});
```
Python unit tests are synchronous; inject `now=` / `embed=` instead of sleeping.

**Error Testing:**
```python
with pytest.raises(MaterialNotReadyError):
    index_material_chunks(materials=repo, chunks=chunks, material_id=1, ...)

with pytest.raises(ValidationError):
    EmbeddingResultDto(vector=[0.1, 0.2], model_id="x", input_hash="y")
```

```javascript
test("shows vote error state and recovers on retry", async ({ page }) => {
  await page.goto("/voting?simulateError=1");
  // ... assert data-state=error, role=alert, then retry to success
});
```

**Composition smoke:**
```python
# tests/unit/test_composition_container.py
app = build_in_memory_container([material])
published = app.publish(42)
chunks = app.index(42, embedding_model_id="foundry-embed-v1", embed=lambda _t: [0.0] * 1024)
hits = app.search(query_embedding=[0.0] * 1024, query_text="Alpha")
```

## Where to Add New Tests

| Change type | Put test here | Style |
|-------------|---------------|--------|
| Domain / use-case behavior | `tests/unit/test_<feature>.py` | pytest + `InMemory*` fakes |
| New port | Fake in `tests_support/in_memory.py` + use-case unit test | No network |
| New DTO field/validation | `tests/unit/test_<dto_area>.py` | Construct model / `ValidationError` |
| Migration schema contract | Extend `test_schema_migration_contract.py` or sibling | Read SQL text |
| React user-visible flow | `tests/web-app.spec.js` (or new `*.spec.js` + project in config) | Playwright roles/labels |
| Design-frontend static UI | `tests/design-frontend.spec.js` | Playwright against `design-frontend/pages/` |

**Prescriptive workflow:**
1. Write the minimal failing test (unit or Playwright as appropriate)
2. Run only that test; confirm red for the right reason
3. Implement minimal production code
4. Re-run the new test, then the full relevant suite (`test:unit` and/or Playwright project)
5. Refactor only while green

**CI:** Not detected (no `.github/workflows` in repo) — run suites locally before merge.

---

*Testing analysis: 2026-09-19*
