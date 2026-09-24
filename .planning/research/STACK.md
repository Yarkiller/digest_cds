# Stack Research

**Domain:** YouTube captions → LLM article → Supabase draft ingestion (CLI)
**Project:** Digest CDS v1.1 (ingestion only — not v1 app stack)
**Researched:** 2026-09-24
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | ≥3.12 (workspace) | Runtime for `data-collection` + new `ingestion-service` | Already locked in root `pyproject.toml`; matches backend / supabase-integration |
| uv workspace member `ingestion-service/` | new package | Thin CLI one-shot composition root | Keeps YouTube/LLM/CLI out of FastAPI; wiring only in this package’s composition |
| `data-collection` (expand) | 0.1.0 + new deps | Ports/DTOs + external adapters (captions, LLM) | Existing bounded context for external APIs; domain stays free of SDKs |
| `supabase-integration` (reuse + small write extensions) | existing `supabase>=2.31.0,<3` (lock: **2.31.0**) | `service_role` PostgREST writes to `materials` + `digest_shortlist_*` | Sync `create_service_role_client` already ships; RLS bypass required for draft insert |
| `youtube-transcript-api` | **1.2.4** (pin `>=1.2.0,<2`) | Fetch captions/subtitles by `video_id` | Locked choice for MVP; no Whisper/FoundryModels; no browser/Selenium |
| `openai` (official Python SDK) | **3.19.2** (pin `>=3.0,<4` or exact) | DeepSeek via OpenAI-compatible client | DeepSeek docs prescribe `OpenAI(api_key=…, base_url="https://api.deepseek.com")` |
| DeepSeek Chat Completions | `base_url=https://api.deepseek.com`, model **`deepseek-flash`** (env-overridable) | LLM: transcript → markdown article | Official current models: `deepseek-flash`, `deepseek-v4-pro`; ADR-0002 temporary bend |
| Typer | **0.27.2** (pin `>=0.21,<0.28`) | CLI surface (`ingest <url> --template lecture\|podcast`) | Type-hint CLI, uv-friendly, thin; no need for Click alone or argparse sprawl |
| Pydantic v2 | existing **2.13.5** (lock) / `>=2.10` | DTO validation in `data-collection` | Already the DTO standard (`YoutubeSourceDto`, `ArticleAssistDto`, …) |
| Markdown prompt templates | package data files `lecture.md`, `podcast.md` | Prompt bodies for TemplateKind | Files on disk, versionable; no YAML UI this milestone |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `httpx` | **0.28.1** (already locked) | Optional YouTube oEmbed / lightweight metadata HTTP | Title/channel without YouTube Data API key; keep off critical path if captions-only UAT is enough |
| `requests` | transitive via `youtube-transcript-api` | Caption HTTP transport | Do not add directly; comes with transcript lib |
| `httpx2` | transitive via `openai` 3.x (`httpx2>=2.12,<3`) | OpenAI SDK HTTP stack | Do not import in app code; coexistence with backend `httpx` is fine (different package name) |
| `defusedxml` | transitive via `youtube-transcript-api` | Safe XML parsing of timedtext | Do not add directly |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `uv` | Workspace deps + `uv run` CLI | Add `ingestion-service` to `[tool.uv.workspace].members` and `[tool.uv.sources]` |
| `pytest` | Unit tests for DTOs, adapters (fakes), CLI argument parsing | Red–Green–Refactor; network tests marked integration / skipped in CI |
| Env vars (names only) | Secrets for CLI | `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL` (default `https://api.deepseek.com`), `DEEPSEEK_MODEL` (default `deepseek-flash`), `SUPABASE_URL`, `SUPABASE_SECRET_KEY` (service_role — same name as v1 backend) |

## Installation

```bash
# From repo root — after creating ingestion-service/pyproject.toml and expanding data-collection deps

# data-collection adapters
uv add --package data-collection "youtube-transcript-api>=1.2.0,<2" "openai>=3.0,<4"

# optional metadata helper (prefer workspace httpx already present)
uv add --package data-collection "httpx==0.28.1"

# new CLI package (workspace member)
# pyproject: depends on data-collection, supabase-integration, typer
uv add --package ingestion-service "typer>=0.21,<0.28"
uv add --package ingestion-service --editable data-collection supabase-integration

# root workspace: append ingestion-service to members + sources, then
uv sync

# run (example)
uv run --package ingestion-service ingest "https://www.youtube.com/watch?v=…" --template lecture
```

### Workspace integration map

```text
digest-cds (uv workspace)
├── backend/                 # UNCHANGED for v1.1 (reader API)
├── web/                     # UNCHANGED (admin UI already lists drafts)
├── data-collection/         # EXPAND: DTOs/ports + YouTube caption + DeepSeek adapters
├── supabase-integration/    # REUSE sync service_role client; ADD draft+enqueue write path
└── ingestion-service/       # NEW: Typer CLI + composition + templates/*.md
```

**Dependency direction (required):**

- `ingestion-service` → `data-collection` (DTOs/adapters) + `supabase-integration` (writes)
- `data-collection` must **not** import `supabase` / FastAPI
- `supabase-integration` must **not** import `openai` / `youtube_transcript_api`
- Backend/SPA remain readers of `materials` / shortlist; no new HTTP ingestion routes

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `youtube-transcript-api` 1.2.x instance `.fetch()` | Older static `YouTubeTranscriptApi.get_transcript` (0.6.x) | Never — API shape changed; pin ≥1.2 and use instance methods |
| Official `openai` SDK + DeepSeek `base_url` | Raw `httpx` against `/chat/completions` | Only if openai 3.x / httpx2 causes lockfile pain; lose typed SDK |
| Official `openai` 3.19.x | Pin `openai==2.11.0` (still httpx-based in older line) | If uv cannot resolve `httpx2` alongside other tools; verify DeepSeek still works |
| Typer | Plain `argparse` or Click alone | argparse OK for 1-command CLI; Typer preferred for options/`--template` enum ergonomics |
| Sync `create_service_role_client` | `create_async_client` / AsyncPostgREST | CLI one-shot does not need async; sync matches existing repositories |
| YouTube oEmbed via httpx | YouTube Data API (`google-api-python-client`) | Only if UAT requires channel/duration beyond title; needs API key + quota |
| DeepSeek `deepseek-flash` | `deepseek-v4-pro` | Higher quality / cost; use via `DEEPSEEK_MODEL` when drafts need more polish |
| File templates `.md` | Jinja2 / LangChain PromptTemplate | Only if templating logic grows; overkill for 1–2 static prompts |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Whisper / `openai-whisper` / `faster-whisper` / torch | Explicitly OUT; heavy, GPU, bends ADR-0002 differently | Captions via `youtube-transcript-api` |
| FoundryModels transcription/summarization client this milestone | Deferred revisit after DeepSeek MVP | `openai` → DeepSeek; keep Foundry DTOs unused |
| `yt-dlp` / `youtube-dl` / media download | Content contract: no media-as-material; captions suffice | Transcript API only |
| LangChain / LlamaIndex / Haystack / LiteLLM | Extra abstraction for one provider + two templates | Thin adapter wrapping `OpenAI(...).chat.completions.create` |
| Celery / APScheduler / Prefect / cron-in-process | Scheduler OUT of v1.1 | Operator runs CLI once per URL |
| FastAPI ingestion routes / new SPA services | HTTP API OUT; admin already reads drafts | CLI → Supabase only |
| SMTP / StubMailer changes / auto-publish | Send/publish OUT | Leave Phase 5 admin path untouched |
| Anthropic / other LLM SDKs | One LLM only for MVP | DeepSeek via OpenAI SDK |
| `supabase` async client for ingestion | Existing adapters are sync; dual stack adds complexity | Sync `create_service_role_client(url, SUPABASE_SECRET_KEY)` |
| Storing raw transcript as `materials.body_markdown` | Material = agent-prepared article only | LLM markdown → `materials`; optional `source_texts` only as pipeline provenance if needed later |
| Pinning `youtube-transcript-api==0.6.x` docs patterns | Deprecated API (`get_transcript` classmethod) | `YouTubeTranscriptApi().fetch(video_id, languages=[...])` |

## Stack Patterns by Variant

**If captions missing (`TranscriptsDisabled` / `NoTranscriptFound`):**
- Fail the CLI with a clear non-zero exit; do not fall back to Whisper
- Because Whisper is out of scope; pick another video for UAT

**If DeepSeek / corporate network blocks public LLM:**
- Keep adapter behind a port (`ArticleAssist` / `LlmCompleter`) so FoundryModels can replace `base_url` later
- Because ADR-0002 revisit is planned; do not hard-code DeepSeek types into domain

**If video title is needed for slug/provenance without Data API:**
- Use YouTube oEmbed (`https://www.youtube.com/oembed?url=…&format=json`) via existing `httpx`
- Because no API key; sufficient for draft slug + `provenance_label`

**If shortlist has no open batch (`sent_at IS NULL`):**
- CLI creates/ensures an unsent `digest_shortlist_batches` row then inserts item, **or** fails with operator guidance
- Because admin `/admin/digest` needs an item in a current batch for UAT visibility

**If running on the shared Cloud.ru VM:**
- Load `SUPABASE_URL` + `SUPABASE_SECRET_KEY` + `DEEPSEEK_API_KEY` from env/secret store only
- Because service_role must never enter `web/` or Vite env

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `openai==3.19.2` | Python ≥3.10; workspace ≥3.12 | Depends on **`httpx2`**, not `httpx` — no conflict with backend `httpx==0.28.1` |
| `openai` + DeepSeek | `base_url="https://api.deepseek.com"` | Official DeepSeek “Your First API Call”; model ids currently `deepseek-flash` / `deepseek-v4-pro` (legacy flash aliases still accepted) |
| `youtube-transcript-api==1.2.4` | Python ≥3.8,<3.15 | Instance API: `YouTubeTranscriptApi().fetch(video_id, languages=("ru","en"))` → `FetchedTranscript`; `.to_raw_data()` → `{text,start,duration}` |
| `supabase==2.31.0` | Existing `create_client` sync | Continue sync service_role; insert/upsert via `.table(...).insert(...).execute()` |
| `typer==0.27.2` | Python ≥3.10 | Pair with existing pydantic ≥2.10 |
| `pydantic==2.13.5` | `openai` / DTO layer | Already satisfied by lockfile |
| New DTOs vs Foundry DTOs | Coexist | Keep `TranscriptResultDto` / `ArticleAssistDto` as Foundry-shaped; add ingestion-specific `Transcript`, `VideoMetadata`, `MaterialDraft`, `TemplateKind` without removing Foundry stubs |

### youtube-transcript-api API shape (verified)

```python
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

ytt = YouTubeTranscriptApi()
fetched = ytt.fetch("VIDEO_ID", languages=["ru", "en"])  # video_id, NOT full URL
text = " ".join(snippet.text for snippet in fetched)
# or: fetched.to_raw_data()  # list[dict]: text / start / duration
```

Map adapter exceptions → domain/application errors at the boundary (`TranscriptsDisabled`, `NoTranscriptFound`, `IpBlocked` / `RequestBlocked`, `PoTokenRequired`).

### DeepSeek via OpenAI SDK (verified)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
response = client.chat.completions.create(
    model=os.environ.get("DEEPSEEK_MODEL", "deepseek-flash"),
    messages=[
        {"role": "system", "content": system_from_template},
        {"role": "user", "content": transcript_text},
    ],
    stream=False,
)
markdown = response.choices[0].message.content
```

Optional thinking mode (`reasoning_effort` / `extra_body={"thinking": …}`) is **not required** for MVP article drafts; keep disabled unless quality UAT demands it (cost/latency).

### Supabase service_role write path (verified against repo)

```python
from supabase_integration import create_service_role_client

client = create_service_role_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SECRET_KEY"],  # service_role; same as backend live composition
)
# insert materials status='draft'; enqueue digest_shortlist_items on current unsent batch
client.table("materials").insert({...}).execute()
client.table("digest_shortlist_items").insert({...}).execute()
```

Prefer extending `supabase-integration` adapters (new enqueue/create-draft methods) over raw table calls from the CLI. Existing `SupabaseMaterialRepository.save` upserts by id — ingestion likely needs **insert-without-id** returning generated `id` for shortlist FK. Sync client only; do not introduce async for this milestone.

Schema already supports drafts: `material_status` enum includes `draft`; migration 005 seeds a draft for admin triage. Optional provenance tables (`ingestion_sources`, `source_texts`) exist — use later if needed; MVP write target is `materials` + `digest_shortlist_items`.

## Sources

- Context7 `/jdepoix/youtube-transcript-api` — `fetch`, `FetchedTranscript`, exception catalog (HIGH)
- Context7 `/openai/openai-python` — `OpenAI(base_url=...)`, chat.completions (HIGH)
- Context7 `/websites/api-docs_deepseek` + https://api-docs.deepseek.com/ — base_url, models `deepseek-flash` / `deepseek-v4-pro` (HIGH)
- Context7 `/supabase/supabase-py` — `create_client`, insert patterns; repo already uses sync service_role (HIGH)
- Context7 `/fastapi/typer` — CLI patterns; version listing includes 0.21.1 (MEDIUM docs) + PyPI **0.27.2** (HIGH)
- PyPI JSON (2026-09-24): `youtube-transcript-api==1.2.4`, `openai==3.19.2`, `typer==0.27.2` (HIGH)
- Repo lockfile: `supabase==2.31.0`, `httpx==0.28.1`, `pydantic==2.13.5` (HIGH)
- Repo: `supabase_integration.client.create_service_role_client`, migrations `001`/`005` materials + shortlist (HIGH)

## Confidence notes

| Claim | Confidence | Caveat |
|-------|------------|--------|
| Captions library + instance API | HIGH | YouTube may IP-block datacenter IPs (`IpBlocked` / `PoTokenRequired`) — UAT from residential/operator network |
| DeepSeek OpenAI-compatible client | HIGH | Model id renamed to `deepseek-flash`; do not hard-code retired `deepseek-chat` as sole default |
| openai 3.x + httpx2 in shared uv lock | HIGH (deps) / MEDIUM (resolve) | Confirm `uv sync` once; fallback pin openai 2.11.x if lock conflicts |
| Sync service_role writes for drafts | HIGH | Need new insert/enqueue adapter methods; current ShortlistRepository has no enqueue API |

---
*Stack research for: Digest CDS v1.1 YouTube → LLM → Supabase CLI ingestion*
*Researched: 2026-09-24*
*Scope: NEW capabilities only — v1 FastAPI/React/Auth stack not re-researched*
