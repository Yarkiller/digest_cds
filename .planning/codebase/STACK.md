# Technology Stack

**Analysis Date:** 2026-09-19

## Languages

**Primary:**
- JavaScript (ES modules, JSX) — React app in `web/`, Playwright tests in `tests/`, static design reference scripts in `design-frontend/`
- Python 3.12 — workspace packages `backend/`, `data-collection/`, `supabase-integration/` (pinned via `.python-version` and `requires-python = ">=3.12"`)

**Secondary:**
- SQL (Postgres / Supabase) — schema and RLS in `supabase-integration/migrations/001_initial_schema.sql`
- CSS — Tailwind v4 via Vite plugin in `web/`; design tokens in `design-frontend/styles/`
- Markdown — domain docs (`CONTEXT.md`, `docs/`), ADRs (`docs/adr/`)

**Not in use for app source:**
- TypeScript — only `@types/react` / `@types/react-dom` as Vite/React typing aids; app sources are `.jsx` / `.js`
- FastAPI — documented as target HTTP layer in architecture rules and `.scratch/digest-cds/spec.md`; **not** a declared dependency in any `pyproject.toml` yet

## Runtime

**Environment:**
- Node.js — npm scripts and Vite/Playwright (engine not pinned in `package.json`)
- CPython 3.12 — local `.venv/` managed by `uv`
- Browsers for E2E — Chromium via Playwright, cached under `.playwright-browsers/`

**Package Manager:**
- **npm** — root `package.json` + `web/package.json`; lockfiles: `package-lock.json`, `web/package-lock.json` (lockfileVersion 3)
- **uv** — Python workspace root `pyproject.toml` + `uv.lock`; rule: use `uv add` / `uv sync` / `uv run` only (see `.cursor/rules/python-uv.mdc`)

## Frameworks

**Core:**
- React 19.2.8 — UI (`web/src/`)
- React Router DOM 7.18.3 — client routing (`web/src/App.jsx`)
- Vite 8.2.2 — build/dev server (`web/vite.config.js`, host `127.0.0.1:5173`)
- Tailwind CSS 4.3.3 + `@tailwindcss/vite` — styling
- Pydantic 2.13.5 — external-source / ML DTOs in `data-collection/`

**Testing:**
- Playwright `@playwright/test` 1.62.1 — E2E for `design-frontend` and `web` (`playwright.config.js`, `tests/`)
- pytest 9.1.1 — Python unit tests (`tests/unit/`, config in root `pyproject.toml`)

**Build/Dev:**
- Vite (`npm run dev` / `build` / `preview`)
- oxlint 1.79.0 — JS lint (`web/.oxlintrc.json`, `npm run lint --prefix web`)
- `serve@14.2.4` (npx) — static design-frontend server on port 8765
- `uv_build` — Python package build backend for workspace members

## Key Dependencies

**Critical:**
- `react` / `react-dom` 19.2.8 — SPA delivery
- `react-router-dom` 7.18.3 — routes: `/`, `/voting`, `/knowledge`, `/materials/:id`
- `pydantic` 2.13.5 — `YoutubeSourceDto`, Foundry result DTOs, `TextImportDto` in `data-collection/src/data_collection/dto/`
- Workspace packages `backend`, `data-collection`, `supabase-integration` — Ports & Adapters layout (see architecture rules)

**Infrastructure:**
- Self-hosted Supabase (PostgreSQL + `vector` + `pg_trgm`) — schema owned by `supabase-integration/`; **no** `supabase-py` / `@supabase/supabase-js` in lockfiles yet
- In-memory fakes — `backend/src/backend/tests_support/in_memory.py` wired by `backend/src/backend/composition/container.py` until real adapters land
- Playwright browsers — project-local `.playwright-browsers/` via `scripts/ensure-playwright-browsers.cjs`

**Explicitly absent from current lockfiles (planned):**
- FastAPI / Uvicorn HTTP stack
- `httpx` / YouTube Data API client SDKs
- FoundryModels / Cloud.ru SDK clients
- Supabase official client libraries

## Configuration

**Environment:**
- `.env` present at repo root (gitignored via `.gitignore`) — contains local secrets; **do not commit or quote values**
- `.env.*` also ignored; no committed `.env.example` detected
- Application Python/JS code currently has **no** `os.environ` / `VITE_*` reads — secrets are reserved for future adapters and VM deploy (ADR-0002, ADR-0004)
- Playwright: `PLAYWRIGHT_BROWSERS_PATH` set in `playwright.config.js` to `.playwright-browsers/`
- CI flag: `process.env.CI` controls `reuseExistingServer` in Playwright webServers

**Build:**
- `web/vite.config.js` — React + Tailwind plugins; fixed host/port
- Root `pyproject.toml` — uv workspace members, pytest `testpaths = ["tests/unit"]`
- Member `pyproject.toml` files under `backend/`, `data-collection/`, `supabase-integration/`
- `web/.oxlintrc.json` — React hooks rules

**Key configs required (runtime target, per ADRs — names not yet coded):**
- Supabase base URL and service/anon keys (configurable; instance documented as `https://knowledge-db.ru/`)
- FoundryModels credentials (Cloud.ru contour)
- YouTube Data API credentials (when adapter is implemented)
- Corporate SMTP settings (digest mail — post-homework / production)

## Platform Requirements

**Development:**
- Python ≥ 3.12 + `uv` (`uv sync`, `uv run pytest`)
- Node.js + npm (`npm install`, `npm install --prefix web`)
- Optional: WSL for Cursor Origin git auth (`docs/agents/git-origin.md`)
- Ports: Vite `5173` (dev) / `5174` (Playwright web project); design static `8765`

**Production:**
- Application VM on **Cloud.ru** (ADR-0002)
- Separate VM for **self-hosted Supabase** via Docker Compose (ADR-0004); managed Supabase Cloud and managed Postgres Cloud.ru are out of scope
- ML calls stay in Cloud.ru **FoundryModels** (no public foreign LLM/Whisper APIs)
- Current homework UI (`web/`) runs as a static SPA with mock data; production auth/SMTP/Foundry wiring is explicitly out of ДЗ scope per `docs/digest-cds/technical_specification.md`

## Workspace Layout (stack-relevant)

| Path | Role |
|------|------|
| `web/` | Vite + React + Tailwind SPA |
| `design-frontend/` | Static UI Concept 3 reference (HTML/CSS/JS) |
| `backend/` | Domain, ports, use-cases, composition (no FastAPI yet) |
| `data-collection/` | External API DTOs (YouTube, Foundry, text import) |
| `supabase-integration/` | Migrations + future Supabase adapters |
| `tests/` | Playwright E2E + `tests/unit` pytest |
| `docs/adr/` | Architecture decisions binding stack choices |

---

*Stack analysis: 2026-09-19*
