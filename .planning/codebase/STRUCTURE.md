# Codebase Structure

**Analysis Date:** 2026-09-19

## Directory Layout

```
Digital_CDS/
├── backend/                    # Python domain + application (uv package)
│   └── src/backend/
│       ├── domain/             # Entities, errors
│       ├── application/
│       │   ├── ports/          # Protocol interfaces
│       │   └── use_cases/      # Scenarios
│       ├── composition/        # DI / AppContainer
│       └── tests_support/      # In-memory port fakes
├── data-collection/            # External-API DTOs (uv package)
│   └── src/data_collection/dto/
├── supabase-integration/       # DB adapter package + SQL migrations
│   ├── migrations/
│   └── src/supabase_integration/
├── web/                        # React + Vite production UI
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── data/
│       └── utils/
├── design-frontend/            # Static Editorial UI concept
│   ├── pages/
│   ├── styles/
│   ├── assets/
│   └── scripts/
├── tests/                      # Pytest unit + Playwright E2E
│   └── unit/
├── docs/                       # Specs, ADRs, agent docs
│   ├── adr/
│   ├── agents/
│   └── digest-cds/
├── scripts/                    # Tooling (Playwright browsers)
├── .cursor/rules/              # Always-on agent architecture/TDD rules
├── .agents/skills/             # Project skills (supabase, hallmark, …)
├── .scratch/                   # Local issue tracker markdown
├── .planning/                  # GSD planning artifacts (incl. this map)
├── archive/                    # Archived homework zip / notes
├── CONTEXT.md                  # Domain glossary
├── AGENTS.md                   # Agent entry (TDD, skills pointers)
├── pyproject.toml              # uv workspace root
├── package.json                # Root npm scripts + Playwright
├── playwright.config.js
├── uv.lock
└── .env                        # Local env (exists; secrets — do not read/commit)
```

## Directory Purposes

**`backend/`:**
- Purpose: Core business logic package (`name = "backend"`).
- Contains: Domain, ports, use-cases, composition root, in-memory test adapters.
- Key files: `backend/src/backend/composition/container.py`, `backend/src/backend/domain/material.py`, `backend/pyproject.toml`.

**`data-collection/`:**
- Purpose: Bounded context for inbound external data shapes (YouTube, text import, FoundryModels).
- Contains: Pydantic DTOs only (no live HTTP clients yet).
- Key files: `data-collection/src/data_collection/__init__.py`, `dto/youtube.py`, `dto/foundry.py`, `dto/text_import.py`.

**`supabase-integration/`:**
- Purpose: Postgres/Supabase schema and (future) repository adapters implementing backend ports.
- Contains: SQL migrations; stub public API `migrations_dir()`.
- Key files: `supabase-integration/migrations/001_initial_schema.sql`, `supabase-integration/src/supabase_integration/__init__.py`.

**`web/`:**
- Purpose: Primary React delivery for Digest CDS UI.
- Contains: Pages, components, mock data, service boundary, Tailwind styles.
- Key files: `web/src/main.jsx`, `web/src/App.jsx`, `web/vite.config.js`, `web/package.json`.

**`design-frontend/`:**
- Purpose: Canonical static design (Editorial Concept 3); visual/token reference and design E2E target.
- Contains: HTML pages, CSS tokens/layout/components, covers, notebooks assets, `UI-SPEC_3.md`.
- Key files: `design-frontend/index.html`, `design-frontend/styles/tokens.css`, `design-frontend/pages/*.html`.

**`tests/`:**
- Purpose: Automated verification — Python unit (pytest) and Playwright E2E.
- Contains: `tests/unit/*.py`, `tests/web-app.spec.js`, `tests/design-frontend.spec.js`.
- Key files: `tests/unit/test_publish_and_index.py`, `tests/unit/test_schema_migration_contract.py`.

**`docs/`:**
- Purpose: Product/tech docs and decision records.
- Contains: ADRs, agent workflow docs, digest-cds specs and responsive evidence.
- Key files: `docs/adr/0004-self-hosted-supabase-on-vm.md`, `docs/agents/domain.md`.

**`scripts/`:**
- Purpose: Repo tooling helpers.
- Contains: Playwright browser cache installer.
- Key files: `scripts/ensure-playwright-browsers.cjs`.

**`.cursor/rules/`:**
- Purpose: Always-applied agent constraints (architecture, TDD, uv).
- Key files: `.cursor/rules/architecture.mdc`, `.cursor/rules/tdd.mdc`.

**`.planning/`:**
- Purpose: GSD maps, plans, research outputs.
- Contains: `codebase/` analysis docs (this folder).

**`.scratch/`:**
- Purpose: Local markdown issues (see `docs/agents/issue-tracker.md`).
- Generated: No (hand-maintained). Committed: Per project policy for scratch issues.

**`archive/`:**
- Purpose: Historical homework artifacts.
- Key files: `archive/README.md`.

## Key File Locations

**Entry Points:**
- `web/src/main.jsx`: React bootstrap.
- `web/src/App.jsx`: Route table (`/`, `/voting`, `/knowledge`, `/materials/:id`).
- `backend/src/backend/composition/container.py`: Application façade (`publish` / `index` / `search`).
- `backend/src/backend/__init__.py`: Public domain exports.
- `data-collection/src/data_collection/__init__.py`: Public DTO exports.
- `design-frontend/index.html`: Static prototype entry.

**Configuration:**
- `pyproject.toml`: uv workspace members, pytest `testpaths = ["tests/unit"]`.
- `backend/pyproject.toml`, `data-collection/pyproject.toml`, `supabase-integration/pyproject.toml`: Per-package metadata.
- `package.json`: Root scripts (`dev`, `test`, `test:unit`, `test:web`, `test:design`).
- `web/package.json`: Vite/React/Tailwind/oxlint.
- `playwright.config.js`: E2E projects and webServers.
- `.python-version`: Python version pin.
- `.env`: Local environment file (existence only — never read secrets into docs).

**Core Logic:**
- `backend/src/backend/domain/material.py`: Material entity and publish rules.
- `backend/src/backend/domain/knowledge.py`: Chunk and hit models.
- `backend/src/backend/application/use_cases/publish_material.py`
- `backend/src/backend/application/use_cases/index_material_chunks.py`
- `backend/src/backend/application/use_cases/search_knowledge.py`
- `backend/src/backend/application/ports/material_repository.py`
- `backend/src/backend/application/ports/knowledge_chunk_repository.py`
- `supabase-integration/migrations/001_initial_schema.sql`: Canonical DB schema.

**Frontend logic:**
- `web/src/services/votingApi.js`: Vote API boundary (mock).
- `web/src/data/mock.js`: Issue/materials/voting fixtures.
- `web/src/utils/filters.js`, `web/src/utils/voting.js`: Presentation helpers.

**Testing:**
- `tests/unit/`: pytest (composition, publish/index, search, DTOs, migration contract).
- `tests/web-app.spec.js`: Playwright against Vite app.
- `tests/design-frontend.spec.js`: Playwright against static design.
- `backend/src/backend/tests_support/in_memory.py`: Shared fakes for unit tests.

**Domain / product docs:**
- `CONTEXT.md`: Glossary and language rules.
- `docs/digest-cds/`: Specs, user stories, development notes.
- `docs/adr/`: Architecture Decision Records.

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g. `publish_material.py`, `knowledge_chunk_repository.py`).
- React components/pages: `PascalCase.jsx` (e.g. `VotingPage.jsx`, `AppShell.jsx`).
- Frontend utils/services/data: `camelCase.js` (e.g. `votingApi.js`, `mock.js`).
- SQL migrations: numbered prefix `NNN_description.sql` under `supabase-integration/migrations/`.
- ADRs: `NNNN-kebab-title.md` under `docs/adr/`.
- Playwright specs: `*.spec.js` under `tests/`.
- Pytest: `test_*.py` under `tests/unit/`.

**Directories:**
- Python packages under `src/<package_name>/` (src layout for all uv members).
- Frontend feature folders by role: `components/`, `pages/`, `services/`, `data/`, `utils/` — not feature-sliced folders yet.
- Design pages mirror product routes: `design-frontend/pages/issue.html`, `voting.html`, `knowledge.html`, etc.

**Symbols:**
- Python: `snake_case` functions; `PascalCase` classes/protocols/enums; domain errors end with `Error`.
- React: default-export page/component functions in `PascalCase`.
- Ports: noun + `Repository` (`MaterialRepository`).
- Use-cases: verb phrases as module and function names (`publish_material`).

## Where to Add New Code

**New domain behavior (publish/search/rules):**
- Primary code: `backend/src/backend/domain/` and/or `backend/src/backend/application/use_cases/`
- New port (if I/O needed): `backend/src/backend/application/ports/<name>.py`
- Wire: `backend/src/backend/composition/container.py`
- Tests first: `tests/unit/test_<behavior>.py` with in-memory fakes in `backend/.../tests_support/`
- Do **not** put SDK calls in domain/use-cases.

**New HTTP API endpoint (when introducing FastAPI):**
- Routers: create `backend/src/backend/interface/http/` (thin handlers).
- Compose dependencies only in `composition/`.
- Tests: unit for use-case; separate integration tests for HTTP if added.

**New Supabase / Postgres persistence:**
- Schema: new migration under `supabase-integration/migrations/`.
- Adapter implementing ports: under `supabase-integration/src/supabase_integration/` (public export via package `__init__.py`).
- Contract tests: extend `tests/unit/test_schema_migration_contract.py` or add sibling unit/integration tests.
- Wire adapter in composition (replace `InMemory*` when ready).

**New external API (YouTube, FoundryModels, …):**
- DTOs / validation: `data-collection/src/data_collection/dto/`
- Export from `data-collection/src/data_collection/__init__.py`
- Live client/adapter: same package (not backend domain); map errors at adapter edge.
- Tests: `tests/unit/test_*_dto.py` pattern already used.

**New UI page or component:**
- Page: `web/src/pages/<Name>Page.jsx` + route in `web/src/App.jsx`
- Component: `web/src/components/<Name>.jsx`
- API calls: `web/src/services/<name>Api.js` only
- Shared pure helpers: `web/src/utils/`
- Temporary fixtures: `web/src/data/` (prefer replacing with services when backend exists)
- Design alignment: update or reference matching `design-frontend/pages/` + tokens
- E2E: extend `tests/web-app.spec.js` (and design project if visual contract changes)

**New ADR / domain term:**
- ADR: `docs/adr/NNNN-title.md`
- Glossary: `CONTEXT.md` (single source; see `docs/agents/domain.md`)

**Utilities:**
- Prefer ownership inside a bounded context (backend / web / data-collection).
- Avoid new root-level “common utils” packages without a clear owner.
- Root `scripts/` is for tooling only, not business logic.

## Special Directories

**`web/dist/`:**
- Purpose: Vite production build output.
- Generated: Yes.
- Committed: No (build artifact).

**`node_modules/`, `.venv/`, `.pytest_cache/`, `test-results/`, `.playwright-browsers/`:**
- Purpose: Dependencies, caches, test artifacts, local browsers.
- Generated: Yes.
- Committed: No.

**`.env`:**
- Purpose: Local secrets and environment configuration.
- Generated: No (local).
- Committed: No — never quote contents in docs or commits.

**`.planning/codebase/`:**
- Purpose: Generated architecture maps for GSD planners/executors.
- Generated: By `/gsd-map-codebase`.
- Committed: Yes when orchestrator commits planning artifacts.

**`design-frontend/.hallmark/`:**
- Purpose: Hallmark design skill log/metadata.
- Generated: Tooling.
- Committed: As present in tree.

**Missing planned folders (create when needed, do not invent early):**
- `backend/src/backend/interface/http/` — FastAPI routers.
- `backend/src/backend/infrastructure/` — backend-local adapters if not in sibling packages.
- Live adapter modules inside `supabase-integration` / `data-collection` beyond DTOs/migrations.

## Prescriptive Placement Checklist

| Change type | Put it here |
|-------------|-------------|
| Entity / domain error | `backend/src/backend/domain/` |
| Use-case | `backend/src/backend/application/use_cases/` |
| Port (Protocol) | `backend/src/backend/application/ports/` |
| Wire adapters | `backend/src/backend/composition/` |
| In-memory fake | `backend/src/backend/tests_support/` |
| SQL schema | `supabase-integration/migrations/` |
| External DTO | `data-collection/src/data_collection/dto/` |
| React page | `web/src/pages/` |
| React component | `web/src/components/` |
| Frontend API call | `web/src/services/` |
| Unit test (Python) | `tests/unit/` |
| E2E test | `tests/*.spec.js` |

---

*Structure analysis: 2026-09-19*
