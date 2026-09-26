---
last_mapped_commit: 427615dc0eb6b133900513db4b0f240398db862f
---
<!-- refreshed: 2026-09-26 -->
# Testing Patterns

**Analysis Date:** 2026-09-26

## Test Framework

**Runner:**
- Unit (Python): pytest `>=8.3.0` (root `pyproject.toml` dependency group `dev`)
  - Config: `[tool.pytest.ini_options]` in root `pyproject.toml`
  - `testpaths = ["tests/unit"]`, `pythonpath = ["."]`
  - Collects only `tests/unit/*.py` (JS unit files and Playwright specs are not collected)
- Unit (JavaScript): Node built-in **`node:test`** + `node:assert/strict`
  - **Not** wired into `npm test`; run per file: `node --test <path>`
  - No Vitest / Jest in the repo
- E2E / UI: Playwright `@playwright/test` `^1.62.1` (root `package.json`)
  - Config: `playwright.config.js`

**Assertion Library:**
- pytest built-in `assert` / `pytest.raises`
- Playwright `expect` from `@playwright/test`
- Node `assert` / `assert/strict` for JS unit tests
- Pydantic `ValidationError` for DTO rejection cases

**Run Commands:**
```bash
npm test                      # All Playwright projects
npm run test:web              # Playwright project `web` only
npm run test:design           # Playwright project `design-frontend` only
npm run test:unit             # uv run pytest (tests/unit/*.py only)
uv run pytest                 # Same Python unit suite
uv run pytest tests/unit/test_cast_vote.py   # Single file
npx playwright test --project=web tests/web-app.spec.js
node --test tests/unit/test_knowledge_api.js
node --test web/src/services/emailDomain.test.js
node tests/unit/test_razbor_notebook_ui_copy.js   # custom script (not node:test)
```

**Browser install (Playwright):**
```bash
npm run playwright:install    # scripts/ensure-playwright-browsers.cjs
```
Browsers cache under `.playwright-browsers` via `PLAYWRIGHT_BROWSERS_PATH` in `playwright.config.js`.

## Test File Organization

**Location:**
- Python unit: separate tree `tests/unit/*.py` (not co-located under `src/`)
- JS unit: `tests/unit/*.js` and occasional colocated `web/src/**/*.test.js`
- E2E: `tests/*.spec.js`
- Shared fakes: `backend/src/backend/tests_support/` (importable package, not under `tests/`)

**Naming:**
- Python: `test_<subject>.py` — e.g. `test_cast_vote.py`, `test_http_voting.py`, `test_supabase_vote_repository_contract.py`
- Functions: `test_<behavior>_...` describing outcome; annotate `-> None`
- E2E: `<surface>.spec.js` matched by Playwright `testMatch`
- JS unit: `test_<subject>.js` or `*.test.js`

**Structure:**
```
tests/
├── unit/                          # pytest + node:test (mixed)
│   ├── test_*.py                  # ~43 Python unit / HTTP / contract files
│   └── test_*.js                  # FE pure-module unit tests
├── web-app.spec.js
├── auth.spec.js
├── knowledge.spec.js
├── razbory.spec.js
├── admin.spec.js
└── design-frontend.spec.js
web/src/services/emailDomain.test.js   # colocated node:test
```

**Categories (Python under `tests/unit/`):**
| Category | Examples |
|----------|----------|
| Use-case / domain | `test_cast_vote.py`, `test_publish_and_index.py`, `test_search_knowledge.py`, `test_send_digest.py`, `test_razbor_use_cases.py` |
| HTTP (FastAPI `TestClient`) | `test_http_voting.py`, `test_http_me.py`, `test_http_admin.py`, `test_cors.py`, `test_request_id.py` |
| Supabase adapter contracts | `test_supabase_*_contract.py` (fake client chain + source/SQL asserts; no live DB) |
| Composition / wiring | `test_composition_container.py`, `test_live_container_wiring.py` |
| DTO validation | `test_foundry_dtos.py`, `test_youtube_source_dto.py`, `test_text_import_dto.py` |
| Auth / JWT infra | `test_jwt_verify.py`, `test_auth_email_domain.py` |
| Migration / schema | `test_schema_migration_contract.py`, `test_phase5_migration_005.py` |
| Meta / env | `test_env_example.py`, `test_stub_mailer.py` |

## Test Structure

**Suite Organization (pytest):**
```python
"""cast_vote use-case — confirm one vote, idempotent same-topic (VOTE-01, D-52)."""

from __future__ import annotations

from datetime import datetime, timezone
import pytest
from backend.domain.errors import InvalidVoteError, VoteConflictError
from backend.application.use_cases.cast_vote import cast_vote
from backend.tests_support.in_memory import InMemoryVoteRepository, InMemoryVotingCycleReader


def _open_cycle() -> VotingCycle:
    ...


def test_cast_vote_stores_exactly_one_vote_and_returns_snapshot() -> None:
    votes, cycles = _seeded()
    snapshot = cast_vote(votes, cycles, user_id="u1", topic_id="topic-1", expected_updated_at=None)
    assert snapshot.my_vote.topic_id == "topic-1"
```

**Suite Organization (Node `node:test`):**
```javascript
/**
 * RED→GREEN: knowledgeApi mock search DTO (KNOW-01 / D-59 / D-61).
 * Run: node --test tests/unit/test_knowledge_api.js
 */
const assert = require('node:assert/strict')
const { describe, it } = require('node:test')

describe('mockSearchKnowledge', () => {
  it('returns items without score', async () => {
    const { mockSearchKnowledge } = await import('...')
    const dto = await mockSearchKnowledge({ q: 'RAG' })
    assert.equal(Object.hasOwn(dto, 'items'), true)
  })
})
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
- Module docstring states intended behavior / TDD slice / requirement IDs
- Prefer local factories (`_draft`, `_seeded`, `_mint`, `_client`) over shared pytest fixtures — **no `conftest.py`**
- Annotate Python test functions with `-> None`
- Playwright groups via `test.describe` by flow / UI states / edge cases / responsive
- Prefer role/label locators; use `getByTestId` for state hooks (`confirm-vote`, harness counters)
- HTTP tests mint ES256 JWTs and inject `signing_key_resolver` with in-memory `AppContainer`

## Mocking

**Framework:** Prefer fakes and harnesses over `unittest.mock` / Jest mocks as the default pattern

**Patterns:**
```python
# In-memory Protocol fakes (preferred for ports)
from backend.tests_support.in_memory import (
    InMemoryMaterialRepository,
    InMemoryVoteRepository,
    InMemoryProfileRepository,
)
from backend.composition.container import build_in_memory_container

app = build_in_memory_container([...])
# Callable stubs for side effects
index_material_chunks(..., embed=lambda text: [0.02] * 1024)
```

```python
# Supabase contract: fake table/query chain (no network)
class _FakeQuery: ...
class _FakeTable: ...
```

```javascript
// Frontend API harness for E2E error paths (not Jest mocks)
import { armFailNextVoteSubmit, submitVote } from '../services/votingApi.js'
// Or arm via URL: /voting?simulateError=1 (VotingPage)
// Or page.addInitScript(() => { window.__DIGEST_*__ = ... })
```

**What to Mock / Fake:**
- Repository ports → `InMemory*` in `backend/src/backend/tests_support/in_memory.py`
- Live composition wiring → `MagicMock` / `monkeypatch` only in `test_live_container_wiring.py`
- Embedding / external compute → lambda or simple callable injected into use-case
- Vote / API failure → service harness (`armFailNextVoteSubmit`, query params, `window.__DIGEST_*__`)
- Playwright web server forces `VITE_USE_MOCKS=true` (offline E2E)

**What NOT to Mock:**
- Domain entities and pure use-case logic — exercise real `Material`, `cast_vote`, etc.
- Pydantic DTO validation — construct real models; assert `ValidationError`
- Accessibility-visible UI behavior in Playwright — assert real DOM roles/text
- Do not write “unit” tests that hit live Supabase/network without an explicit integration marker (none configured; live proof is manual via runbook)

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
# HTTP helper pattern (per-file; duplicated across test_http_*.py)
def _mint(sub: str = "user-1", email: str = "user@example.com") -> str: ...
def _client(container=None) -> TestClient: ...
```

**Location:**
- Factories: co-located in the test module
- Shared fakes: `backend/src/backend/tests_support/in_memory.py`
- Frontend demo data: `web/src/data/mock.js` (consumed by app + E2E when mocks enabled)
- Pure FE logic extracted for Node tests: e.g. `web/src/services/adminPreviewComposition.js`
- Contract fixtures: SQL under `supabase-integration/migrations/` read as text; adapter source read for import-boundary asserts

## Coverage

**Requirements:** None enforced (no `pytest-cov`, Istanbul, or coverage threshold in `pyproject.toml` / CI)

**View Coverage:**
```bash
# Not configured — if adding later, prefer:
# uv run pytest --cov=backend --cov=data_collection --cov=supabase_integration
```

**TDD policy (mandatory):** Red → Green → Refactor. No production code without a failing test first (see `.cursor/rules/tdd.mdc`, `AGENTS.md`). Exceptions only for configs/generated/prototypes with explicit agreement.

**Note:** “Coverage” in `.planning/` often means requirement/decision coverage, not line coverage tooling.

## Test Types

**Unit Tests (Python):**
- Scope: domain entities, use-cases with in-memory ports, Pydantic DTOs, JWT verify, composition root, migration SQL contracts, AST/import boundary checks
- Approach: real domain code + fakes; no HTTP server for pure use-case tests
- Files: `tests/unit/test_*.py`
- Run: `uv run pytest` / `npm run test:unit`

**Unit Tests (JavaScript):**
- Scope: mock API DTO shapes, pure utils (`markdownToc`), admin preview composition, email domain helper, copy-string contracts
- Runner: `node --test` (or plain `node` for custom scripts)
- **Not** included in `npm test` or `npm run test:unit`

**HTTP Tests (in-process):**
- FastAPI `TestClient` + `build_in_memory_container()` + minted JWT
- Files: `tests/unit/test_http_*.py`, `test_cors.py`, `test_request_id.py`
- Still under pytest `tests/unit` — treated as unit/API, not live integration

**Contract Tests:**
- Supabase adapters with fake SDK chains + optional migration/source string asserts
- Files: `tests/unit/test_supabase_*_contract.py`, `test_schema_migration_contract.py`, `test_phase5_migration_005.py`
- Offline; assert no FastAPI imports leak into adapters where checked

**Integration Tests (live DB/network):**
- Not detected as a separate suite; no pytest markers configured
- When adding: mark explicitly, keep out of default `tests/unit` path, and do not call them “unit”
- Manual live proof: `docs/agents/local-platform-runbook.md` (`VITE_USE_MOCKS=false`)

**E2E Tests:**
- Playwright against:
  - React app (`project: web`, baseURL `http://127.0.0.1:5174`) — `web-app|auth|knowledge|razbory|admin.spec.js`
  - Static design concept (`project: design-frontend`, baseURL `http://127.0.0.1:8765`) — `design-frontend.spec.js`
- `webServer` entries start only for selected projects (`playwright.config.js`)
- Web project env forces `VITE_USE_MOCKS=true`
- Covers main flows, UI states (loading/success/error), empty/not-found recovery, auth gates, admin, responsive viewports
- Responsive evidence screenshots under `docs/digest-cds/responsive-evidence/`

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
with pytest.raises(VoteConflictError):
    cast_vote(...)

with pytest.raises(ValidationError):
    EmbeddingResultDto(vector=[0.1, 0.2], model_id="x", input_hash="y")
```

```javascript
test("shows vote error state and recovers on retry", async ({ page }) => {
  await page.goto("/voting?simulateError=1");
  // ... assert data-state=error, role=alert, then retry to success
});
```

**HTTP + JWT:**
```python
# tests/unit/test_http_me.py / test_http_voting.py pattern
token = _mint(sub="user-1")
client = _client()
response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
assert response.status_code == 200
```

**Composition smoke:**
```python
# tests/unit/test_composition_container.py
app = build_in_memory_container([material])
published = app.publish(42)
chunks = app.index(42, embedding_model_id="foundry-embed-v1", embed=lambda _t: [0.0] * 1024)
hits = app.search(query_embedding=[0.0] * 1024, query_text="Alpha")
```

**Import / source boundary:**
```python
# AST or source-text asserts — e.g. test_auth_email_domain.py, contract tests
assert "fastapi" not in adapter_source.lower()
```

## Where to Add New Tests

| Change type | Put test here | Style |
|-------------|---------------|--------|
| Domain / use-case behavior | `tests/unit/test_<feature>.py` | pytest + `InMemory*` fakes |
| New port | Fake in `tests_support/in_memory.py` + use-case unit test | No network |
| New HTTP route | `tests/unit/test_http_<area>.py` | TestClient + JWT + in-memory container |
| New Supabase adapter | `tests/unit/test_supabase_<port>_contract.py` | Fake client + migration/source asserts |
| New DTO field/validation | `tests/unit/test_<dto_area>.py` | Construct model / `ValidationError` |
| Migration schema contract | Extend schema/migration contract tests | Read SQL text |
| Pure FE helper (no Vite) | `tests/unit/test_*.js` or colocated `*.test.js` | `node --test` |
| Mock API shape | `tests/unit/test_*_api.js` | `node --test` + dynamic `import()` if needed |
| React user-visible flow | `tests/<feature>.spec.js` (add to `testMatch` if new name) | Playwright roles/labels |
| Design-frontend static UI | `tests/design-frontend.spec.js` | Playwright against `design-frontend/` |
| Composition / DI wiring | `test_composition_container.py` / `test_live_container_wiring.py` | pytest |

**Prescriptive workflow:**
1. Write the minimal failing test (unit, Node, or Playwright as appropriate)
2. Run only that test; confirm red for the right reason
3. Implement minimal production code
4. Re-run the new test, then the full relevant suite (`test:unit` and/or Playwright project; remember `node --test` for JS units)
5. Refactor only while green

**CI:** Not detected (no `.github/workflows` in repo) — run suites locally before merge. Phase VALIDATION docs list manual commands.

---

*Testing analysis: 2026-09-26*
