<!-- refreshed: 2026-09-19 -->
# Architecture

**Analysis Date:** 2026-09-19

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Delivery / UI                                        │
├──────────────────────────────┬──────────────────────────────────────────────┤
│  React app (Vite)            │  Static design prototype                     │
│  `web/src/`                  │  `design-frontend/`                          │
│  pages → components →        │  HTML + CSS tokens + `scripts/app.js`        │
│  `services/` + `data/mock`   │                                              │
└──────────────┬───────────────┴──────────────────────────────────────────────┘
               │  (planned: HTTP; today: mocks only)
               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Backend application core                                  │
│  `backend/src/backend/`                                                      │
│  interface/http  ← MISSING (no FastAPI routers yet)                          │
│  composition/    → AppContainer                                              │
│  application/    → ports + use_cases                                         │
│  domain/         → Material, KnowledgeChunk, errors                          │
└──────────┬───────────────────────────────┬──────────────────────────────────┘
           │ ports                         │ ports (planned adapters)
           ▼                               ▼
┌──────────────────────────┐    ┌─────────────────────────────────────────────┐
│  In-memory fakes         │    │  Adapter modules (workspace packages)       │
│  `tests_support/`        │    │  `supabase-integration/` — migrations + stub│
│  (current composition)   │    │  `data-collection/` — Pydantic DTOs only    │
└──────────────────────────┘    └──────────────────┬──────────────────────────┘
                                                   ▼
                                    ┌──────────────────────────────┐
                                    │  Supabase / Postgres         │
                                    │  schema: `migrations/`       │
                                    │  (+ FoundryModels / YouTube  │
                                    │   — DTOs defined, no clients)│
                                    └──────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| React shell & routes | Browser UI, navigation, page composition | `web/src/App.jsx`, `web/src/components/AppShell.jsx` |
| UI pages | Issue, voting, knowledge, material views | `web/src/pages/*.jsx` |
| Frontend API boundary | Vote submit (mock); intended home for all backend calls | `web/src/services/votingApi.js` |
| Mock content | Local materials/topics/issue fixtures for UI | `web/src/data/mock.js` |
| Domain entities | Material lifecycle, knowledge chunks/hits, domain errors | `backend/src/backend/domain/` |
| Application ports | `MaterialRepository`, `KnowledgeChunkRepository` protocols | `backend/src/backend/application/ports/` |
| Use-cases | Publish, index chunks, hybrid search | `backend/src/backend/application/use_cases/` |
| Composition root | Wire adapters; expose `publish` / `index` / `search` | `backend/src/backend/composition/container.py` |
| In-memory adapters | Test/local implementations of ports | `backend/src/backend/tests_support/in_memory.py` |
| Data-collection DTOs | Normalized YouTube / text-import / FoundryModels shapes | `data-collection/src/data_collection/dto/` |
| Supabase module | Migrations path public API; schema/RLS SQL | `supabase-integration/src/supabase_integration/__init__.py`, `supabase-integration/migrations/` |
| Design prototype | Canonical Editorial UI (static) | `design-frontend/` |
| Domain glossary | Shared language for agents and product | `CONTEXT.md` |
| Architecture ADRs | Deployment, auth domain, FoundryModels, leaderboard | `docs/adr/` |

## Pattern Overview

**Overall:** Ports & Adapters (hexagonal) with module-level bounded contexts, prescribed by `.cursor/rules/architecture.mdc`.

**Key Characteristics:**
- Dependencies point inward: adapters → application → domain; domain has zero FastAPI/httpx/supabase imports.
- Ports are `typing.Protocol` in `backend/.../application/ports/`.
- External systems live in sibling workspace packages (`supabase-integration`, `data-collection`), not inside domain/use-cases.
- Wiring only in `backend/.../composition/` (`AppContainer`, `build_in_memory_container`).
- Frontend must call backends only through `web/src/services/`; pages must not import Supabase/SDK details.
- TDD (Red–Green–Refactor) is mandatory for behavior changes (`.cursor/rules/tdd.mdc`, `AGENTS.md`).

## Layers

**Domain (`backend/src/backend/domain/`):**
- Purpose: Pure business entities, value objects, domain errors.
- Location: `backend/src/backend/domain/`
- Contains: `Material`, `MaterialStatus`, `KnowledgeChunk`, `KnowledgeHit`, `DomainError` hierarchy.
- Depends on: Standard library only.
- Used by: Application ports, use-cases, composition, public package exports in `backend/src/backend/__init__.py`.

**Application — ports (`backend/src/backend/application/ports/`):**
- Purpose: Persistence/search contracts without implementation.
- Location: `backend/src/backend/application/ports/`
- Contains: `MaterialRepository`, `KnowledgeChunkRepository`.
- Depends on: Domain types only.
- Used by: Use-cases and composition typing.

**Application — use-cases (`backend/src/backend/application/use_cases/`):**
- Purpose: Orchestrate domain rules against ports.
- Location: `backend/src/backend/application/use_cases/`
- Contains: `publish_material`, `index_material_chunks` (+ `split_article_into_atoms`), `search_knowledge`.
- Depends on: Domain + ports (+ injected callables like `embed`).
- Used by: `AppContainer` methods.

**Composition (`backend/src/backend/composition/`):**
- Purpose: Single DI / bootstrap root.
- Location: `backend/src/backend/composition/container.py`
- Contains: `AppContainer`, `build_in_memory_container`.
- Depends on: Ports, use-cases, in-memory adapters.
- Used by: Unit tests (`tests/unit/test_composition_container.py`); future HTTP layer / workers.

**Interface / HTTP:**
- Purpose (target): Thin FastAPI routers mapping HTTP ↔ use-cases.
- Location: Planned at `backend/src/backend/interface/http/` per architecture rule.
- Status: **Not present** — no FastAPI app, routers, or ASGI entrypoint in the repo.

**Infrastructure (backend-local):**
- Purpose (target): Backend-owned adapters if not living in sibling modules.
- Location: Planned at `backend/src/backend/infrastructure/`.
- Status: **Not present** — current adapters are in-memory under `tests_support/`.

**Adapter — supabase-integration:**
- Purpose: DB schema, RLS, eventual Supabase SDK adapters implementing ports.
- Location: `supabase-integration/`
- Contains: `migrations/001_initial_schema.sql`; public `migrations_dir()` only.
- Depends on: Declares workspace dep on `backend` (for future port implementations); no live SDK client yet.

**Adapter — data-collection:**
- Purpose: External API boundary DTOs (YouTube, text import, FoundryModels).
- Location: `data-collection/src/data_collection/`
- Contains: Pydantic models in `dto/`; package exports via `__init__.py`.
- Depends on: `pydantic` only — no HTTP clients yet.

**Frontend delivery (`web/`):**
- Purpose: Production-oriented React UI for homework / product surface.
- Location: `web/src/`
- Contains: Pages, components, services, utils, mock data, Tailwind styles (`index.css`).
- Depends on: React 19, React Router 7, Vite 8 — mock data today, not backend.

**Design delivery (`design-frontend/`):**
- Purpose: Static Editorial concept (UI Concept 3); design tokens source of truth for look.
- Location: `design-frontend/`
- Contains: `pages/*.html`, `styles/*.css`, `scripts/app.js`, assets.
- Depends on: Browser only; served statically for Playwright design project.

## Data Flow

### Primary Request Path (target publish → index → search)

1. Composition builds container with repository adapters (`backend/src/backend/composition/container.py` — `build_in_memory_container`).
2. `AppContainer.publish(material_id)` → `publish_material` loads material, validates via `Material.as_ready`, saves as `READY` (`backend/src/backend/application/use_cases/publish_material.py`).
3. `AppContainer.index(...)` → `index_material_chunks` requires `READY`, splits markdown into atoms, embeds via injected `embed`, replaces chunks (`backend/src/backend/application/use_cases/index_material_chunks.py`).
4. `AppContainer.search(...)` → `search_knowledge` scores chunks (0.7 cosine + 0.3 token FTS), optional role filter, returns `KnowledgeHit` list (`backend/src/backend/application/use_cases/search_knowledge.py`).

### Frontend voting path (current)

1. User selects topic on `web/src/pages/VotingPage.jsx`.
2. Page calls `submitVote(topicId)` in `web/src/services/votingApi.js` (delay + optional fail harness).
3. Service returns `{ topicId, savedAt }` or throws `VoteSubmitError` — no network backend.

### Frontend knowledge / issue path (current)

1. Pages import fixtures from `web/src/data/mock.js`.
2. Filters run client-side via `web/src/utils/filters.js`.
3. No hybrid vector search from backend is wired to the UI yet.

### Ingestion path (schema + DTOs; adapters incomplete)

1. External source shapes enter as DTOs (`YoutubeSourceDto`, `TextImportDto`, Foundry result DTOs) from `data-collection`.
2. Persistence target tables live in `supabase-integration/migrations/001_initial_schema.sql` (`ingestion_sources`, `ingestion_jobs`, `source_texts`, `materials`, `knowledge_chunks`, voting/digest tables).
3. Port implementations that map DTOs → domain → DB are not implemented yet.

**State Management:**
- Backend: Stateless use-cases; state in repository adapters (in-memory dicts today).
- Frontend: Local React `useState` / `useMemo` per page; no global store library.
- Auth profile: Schema expects Supabase `auth.users` → `profiles`; UI shows static display name in `AppShell`.

## Key Abstractions

**Material:**
- Purpose: Publishable article unit (draft → ready) with provenance, roles, tags.
- Examples: `backend/src/backend/domain/material.py`
- Pattern: Frozen dataclass + `MaterialStatus` enum; `assert_publishable` / `as_ready` enforce rules.

**KnowledgeChunk / KnowledgeHit:**
- Purpose: Indexed atomic content for retrieval; search result DTO.
- Examples: `backend/src/backend/domain/knowledge.py`
- Pattern: Frozen dataclasses; embeddings as `list[float]` (dim aligned with Foundry `EMBEDDING_DIM = 1024` in `data-collection`).

**Repository ports:**
- Purpose: Persist materials and chunks without coupling to Supabase.
- Examples: `backend/src/backend/application/ports/material_repository.py`, `knowledge_chunk_repository.py`
- Pattern: `Protocol` with narrow methods (`get`/`save`, `replace_for_material`/`list_all`).

**AppContainer:**
- Purpose: Application façade used by tests and future HTTP/workers.
- Examples: `backend/src/backend/composition/container.py`
- Pattern: Dataclass holding ports; methods delegate to pure use-case functions.

**External DTOs:**
- Purpose: Validate/normalize boundary payloads from YouTube / text import / FoundryModels.
- Examples: `data-collection/src/data_collection/dto/*.py`
- Pattern: Pydantic `BaseModel` with validators; exported via package `__all__`.

**Frontend service module:**
- Purpose: Isolate side effects from UI components.
- Examples: `web/src/services/votingApi.js`
- Pattern: Async functions + typed error class; pages import services, not raw fetch.

## Entry Points

**React SPA:**
- Location: `web/src/main.jsx` → `web/src/App.jsx`
- Triggers: Vite dev (`npm run dev`) or production build (`npm run build`).
- Responsibilities: Mount React, register routes under `AppShell`.

**Python workspace / composition:**
- Location: `backend/src/backend/composition/container.py`
- Triggers: Imports from tests (`tests/unit/`), future ASGI app or CLI.
- Responsibilities: Construct repositories and invoke use-cases.

**Backend public package API:**
- Location: `backend/src/backend/__init__.py`
- Triggers: `from backend import Material, ...`
- Responsibilities: Re-export domain types/errors for consumers.

**Data-collection public API:**
- Location: `data-collection/src/data_collection/__init__.py`
- Triggers: `from data_collection import YoutubeSourceDto, ...`
- Responsibilities: Export DTOs and `EMBEDDING_DIM`.

**Supabase-integration public API:**
- Location: `supabase-integration/src/supabase_integration/__init__.py`
- Triggers: `migrations_dir()` for schema contract tests.
- Responsibilities: Locate SQL migrations directory.

**Design prototype:**
- Location: `design-frontend/index.html` and `design-frontend/pages/*.html`
- Triggers: Static serve on port 8765 (`npm run serve:design` / Playwright).
- Responsibilities: Visual reference and design E2E.

**Root workspace:**
- Location: `pyproject.toml` (uv workspace), `package.json` (npm scripts).
- Triggers: `uv run pytest`, `npm test`, `npm run test:unit`.
- Responsibilities: Orchestrate multi-package tooling.

## Architectural Constraints

- **Threading:** Python use-cases are synchronous pure functions; no async runtime in backend package yet. Frontend is single-threaded browser event loop.
- **Global state:** Frontend vote-fail harness uses module-level `failNextSubmit` in `web/src/services/votingApi.js`. Backend in-memory repos hold mutable dicts/lists inside adapter instances only.
- **Circular imports:** Not observed among backend packages; `supabase-integration` depends on `backend` workspace package; `backend` must not import `supabase_integration` or `data_collection` in domain/use-cases.
- **Module boundaries:** No deep-imports into another package’s internals; use package `__init__.py` / ports. uv workspace members: `backend`, `data-collection`, `supabase-integration` (`pyproject.toml`).
- **Secrets:** `.env` may exist at repo root for local config — never import secrets into domain; never commit values. Note existence only.
- **Missing delivery layer:** Do not invent FastAPI routes inside use-cases; add thin routers under `interface/http` and wire in composition when HTTP is introduced.
- **TDD:** No production behavior without a failing automated test first.

## Anti-Patterns

### SDK or HTTP client inside use-case / domain

**What happens:** Importing `supabase`, `httpx`, or `requests` in `domain/` or `use_cases/`.
**Why it's wrong:** Couples business rules to one vendor; breaks unit tests without network/DB.
**Do this instead:** Define a port in `application/ports/`, implement in `supabase-integration` or `data-collection`, wire in `composition/container.py`.

### Business rules in React pages or FastAPI routers

**What happens:** Scoring, publishability, or ranking computed in `web/src/pages/*.jsx` or (future) fat routers.
**Why it's wrong:** Duplicates domain logic; UI and API diverge.
**Do this instead:** Keep rules in domain/use-cases; UI renders DTOs (e.g. score from `KnowledgeHit`). Client-side filters on mock data in `utils/filters.js` are UI-only until search API exists.

### Bypassing `web/src/services/`

**What happens:** Pages call `fetch`/Supabase client directly.
**Why it's wrong:** Leaks infrastructure into UI; hard to swap mock → real API.
**Do this instead:** Add service modules under `web/src/services/` (pattern already used by `votingApi.js`).

### Wiring outside composition root

**What happens:** `create_client(...)` or repository construction scattered in use-cases or random modules.
**Why it's wrong:** Multiple composition points; adapters become undeleteable without hunting call sites.
**Do this instead:** Only construct adapters in `backend/src/backend/composition/`.

### Treating design-frontend as production app

**What happens:** Shipping features only in static HTML under `design-frontend/`.
**Why it's wrong:** Product path is `web/`; design folder is concept/reference.
**Do this instead:** Implement product behavior in `web/` (and backend packages); keep design-frontend aligned for visuals/E2E reference.

## Error Handling

**Strategy:** Domain exceptions for business failures; frontend typed errors for UX; adapter boundary maps SDK/HTTP failures into domain errors (when adapters exist).

**Patterns:**
- Domain: `MaterialNotFoundError`, `MaterialValidationError`, `MaterialNotReadyError` extend `DomainError` (`backend/src/backend/domain/errors.py`).
- Use-cases raise domain errors; callers (container / future HTTP) translate to status codes.
- Frontend: `VoteSubmitError` with `code` and `retryable` (`web/src/services/votingApi.js`); UI surfaces via `ErrorPanel` (`web/src/components/ErrorPanel.jsx`).
- DTO validation: Pydantic `ValidationError` at data-collection boundary.

## Cross-Cutting Concerns

**Logging:** Not standardized in backend packages yet — no shared logger module. Prefer adding logging at adapter/HTTP edges, not inside pure domain.

**Validation:**
- Domain: `Material.assert_publishable`.
- DTOs: Pydantic field validators in `data-collection`.
- SQL: check constraints and enums in `001_initial_schema.sql`.

**Authentication:**
- Target: Supabase Auth + `profiles` / `app_role` (see migration and ADR-0003 email domain restriction).
- Current UI: No real auth flow; static user label in `AppShell`.

**Design tokens:** Editorial tokens live in `design-frontend/styles/tokens.css`; React app mirrors via Tailwind/CSS variables in `web/src/index.css`.

**Documentation / ADRs:** Product language in `CONTEXT.md`; decisions in `docs/adr/`; agent workflow docs in `docs/agents/`.

---

*Architecture analysis: 2026-09-19*
