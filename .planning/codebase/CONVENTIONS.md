# Coding Conventions

**Analysis Date:** 2026-09-19

## Naming Patterns

**Files:**
- Python packages use snake_case directories and modules: `backend/src/backend/application/use_cases/publish_material.py`, `data_collection/dto/foundry.py`
- React pages: `PascalCase` + `Page` suffix — `web/src/pages/VotingPage.jsx`, `KnowledgePage.jsx`
- React components: `PascalCase` — `web/src/components/ActionButton.jsx`, `ErrorPanel.jsx`
- Frontend utilities/services: camelCase filenames — `web/src/utils/filters.js`, `web/src/services/votingApi.js`
- Unit tests: `test_<behavior>.py` under `tests/unit/`
- Playwright specs: `<area>.spec.js` under `tests/` — `web-app.spec.js`, `design-frontend.spec.js`
- SQL migrations: numbered snake_case — `supabase-integration/migrations/001_initial_schema.sql`

**Functions:**
- Python: snake_case; use-cases are module-level functions, not classes — `publish_material`, `search_knowledge`, `index_material_chunks`
- Private helpers: leading underscore — `_cosine`, `_draft`, `_HEADING`, `_non_blank`
- React components: default-export `PascalCase` function components — `export default function VotingPage()`
- Named JS exports: camelCase — `filterMaterials`, `submitVote`, `armFailNextVoteSubmit`

**Variables:**
- Python locals: snake_case; type annotations required on public signatures
- Prefer immutable domain fields: `tuple[...]` for collections on entities (`roles`, `tags` on `Material`)
- JS: camelCase; UI state strings for interactive buttons: `'idle' | 'loading' | 'error' | 'success'`

**Types:**
- Domain entities: frozen `@dataclass` — `Material`, `KnowledgeChunk`, `KnowledgeHit` in `backend/src/backend/domain/`
- Status enums: `str, Enum` — `MaterialStatus` with lowercase string values (`"draft"`, `"ready"`)
- Ports: `typing.Protocol` with ellipsis stubs — `MaterialRepository`, `KnowledgeChunkRepository` in `backend/src/backend/application/ports/`
- External/API payloads: Pydantic `BaseModel` DTOs in `data-collection/src/data_collection/dto/` — suffix `Dto` (`YoutubeSourceDto`, `EmbeddingResultDto`)
- Domain errors: subclasses of `DomainError` in `backend/src/backend/domain/errors.py`

## Code Style

**Formatting:**
- Python: no Black/Ruff config in repo; follow existing style — `from __future__ import annotations` at top of modules that use modern typing; blank line after imports; 4-space indent
- Frontend: no Prettier config; existing style is **no semicolons**, single quotes for imports/strings in JSX modules (`web/src/App.jsx`, `web/src/main.jsx`)
- Playwright specs use CommonJS `require` and **semicolons** (`tests/web-app.spec.js`) — keep that style in E2E files
- Tailwind utility classes composed via `.join(' ')` arrays on interactive components (`ActionButton.jsx`)

**Linting:**
- Frontend: Oxlint via `npm run lint --prefix web`; config `web/.oxlintrc.json`
  - Plugins: `react`, `oxc`
  - Enforced: `react/rules-of-hooks` as error; `react/only-export-components` as warn (constants allowed)
- Python: no dedicated linter/formatter config detected in workspace `pyproject.toml` files
- TypeScript: Not applicable — app source is JSX/JS (React type packages present for tooling only)

## Import Organization

**Order (Python):**
1. `__future__` annotations (when needed)
2. stdlib (`datetime`, `math`, `re`, `hashlib`, `pathlib`)
3. third-party (`pytest`, `pydantic`)
4. workspace packages (`backend.*`, `data_collection.*`)
5. Local relative imports avoided across packages — use absolute `backend.domain...` / `data_collection.dto...`

**Order (Frontend):**
1. React / library imports (`react`, `react-router-dom`)
2. Local components/pages (`./components/...`, `./pages/...`)
3. Services, utils, mock data (`../services/`, `../utils/`, `../data/`)
4. Side-effect CSS last in entry (`./index.css` in `main.jsx`)

**Path Aliases:**
- Not detected — use relative imports from `web/src/` and package names for Python workspace members
- Python path for tests: root `pythonpath = ["."]` in root `pyproject.toml` so `backend` / `data_collection` resolve under `uv run pytest`

**Module boundaries (prescriptive):**
- Domain/use-cases must not import `supabase`, `httpx`, `fastapi`, or React
- Frontend UI must call APIs only through `web/src/services/` (e.g. `votingApi.js`)
- Wire adapters only in `backend/src/backend/composition/` (`container.py`)
- Public package surfaces use `__all__` — see `backend/src/backend/__init__.py`, `backend/src/backend/composition/__init__.py`

## Error Handling

**Patterns:**
- Raise typed domain exceptions from use-cases/entities — never bare `Exception` for business failures
  - `MaterialNotFoundError`, `MaterialValidationError`, `MaterialNotReadyError` (`backend/src/backend/domain/errors.py`)
- Validation on entities via methods that raise — `Material.assert_publishable()` / `as_ready()`
- Map Pydantic `ValidationError` at DTO boundaries; assert with `pytest.raises(ValidationError)` in unit tests
- Frontend: typed error classes extending `Error` — `VoteSubmitError` with `code` and `retryable` (`web/src/services/votingApi.js`)
- UI catches API errors, normalizes unknown to `VoteSubmitError`, drives button `data-state` and `ErrorPanel` (`web/src/pages/VotingPage.jsx`, `web/src/components/ErrorPanel.jsx`)
- Accessible error UI: `role="alert"` on panels; status text via `role="status"` / `aria-live`

**Do this:**
```python
# use-case
material = repo.get(material_id)
if material is None:
    raise MaterialNotFoundError(material_id)
```

```javascript
// service boundary
throw new VoteSubmitError(message, { code: 'NETWORK', retryable: true })
```

## Logging

**Framework:** Not detected in application code

**Patterns:**
- Prefer domain exceptions and UI error panels over console logging for user-facing failures
- Do not introduce ad-hoc `console.log` / `print` in production paths without an agreed logging approach

## Comments

**When to Comment:**
- Module docstrings for intent / TDD phase — unit tests often start with `"""RED→GREEN: ..."""`
- Composition root docstring — `"""Composition root: wire adapters into use-cases."""` in `container.py`
- Non-obvious helpers — `split_article_into_atoms` documents markdown split behavior
- Frontend: JSDoc on public utils/services when behavior is non-obvious (`filterMaterials`, vote API harness)

**JSDoc/TSDoc:**
- Light JSDoc on service harness and filter helpers; no TSDoc (JSX codebase)
- Python: prefer type annotations over verbose docstrings; short docstrings on public helpers

## Function Design

**Size:**
- Keep use-cases focused on one scenario per function file (`publish_material.py`, `search_knowledge.py`)
- Extract pure helpers in the same module when needed (`_cosine`, `split_article_into_atoms`)
- React page components may own local state + handlers; push pure logic to `web/src/utils/`

**Parameters:**
- Prefer keyword-only args for multi-dependency use-cases: `search_knowledge(*, materials=..., chunks=..., ...)`
- Inject ports as parameters (or via `AppContainer`), never construct clients inside use-cases
- Optional clocks/time: `now: datetime | None = None` for testability (`publish_material`, `index_material_chunks`)
- Callables for side effects: `embed: Callable[[str], list[float]]` rather than embedding SDK inside use-case

**Return Values:**
- Use-cases return domain objects or lists of them (`Material`, `list[KnowledgeChunk]`, `list[KnowledgeHit]`)
- Ports return domain types or `None` for missing (`get` → `Material | None`)
- Avoid `Any` on ports and module boundaries

## Module Design

**Exports:**
- Explicit `__all__` on package public APIs
- React: default export for pages/components; named exports for utils/services/errors
- In-memory fakes live in `backend/src/backend/tests_support/in_memory.py` (structural Protocol duck-typing — no inheritance required)

**Barrel Files:**
- Thin package `__init__.py` re-exports only the public surface
- Use-cases package `__init__.py` may stay empty of re-exports — import use-case modules directly

**Architecture rules to follow when adding code:**
1. New domain concept → `backend/src/backend/domain/`
2. New persistence/search capability → Protocol in `application/ports/`, fake in `tests_support/`
3. New scenario → function in `application/use_cases/` + failing unit test first
4. New external payload shape → Pydantic DTO in `data-collection/src/data_collection/dto/`
5. New UI feature → page/component under `web/src/`; API calls only via `web/src/services/`
6. Wiring → only `backend/src/backend/composition/container.py`

---

*Convention analysis: 2026-09-19*
