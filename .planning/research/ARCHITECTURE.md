# Architecture Research

**Domain:** Digest CDS v1.1 — YouTube captions → LLM article → Supabase draft + shortlist enqueue  
**Researched:** 2026-09-24  
**Confidence:** HIGH (integration boundaries from live codebase); MEDIUM (YouTube/DeepSeek SDK details via Context7)

## Standard Architecture

### System Overview

v1.1 adds a **write-side ingestion deployable** that shares the same Supabase/Postgres as the existing **read/admin HTTP path**. It does not call FastAPI, does not serve readers, and has no SPA/auth knowledge. Integration is **data-plane only** (shared tables).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  EXISTING (v1) — readers + admin triage                                      │
│  web/ ──HTTP──► backend/ (FastAPI) ──ports──► supabase-integration adapters │
│                      composition/live.py (service_role for admin writes)     │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ shared DB
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Supabase / Postgres (self-hosted)                                           │
│  materials | digest_shortlist_* | ingestion_sources | source_texts | …       │
│  RLS on; service_role bypass for privileged writers                          │
└──────────────────────────────────▲──────────────────────────────────────────┘
                                   │ service_role inserts (draft + shortlist)
┌──────────────────────────────────┴──────────────────────────────────────────┐
│  NEW (v1.1) — ingestion write path                                           │
│                                                                              │
│  ingestion-service/ (thin CLI + own composition)                             │
│       │ inbound: argparse/typer URL + TemplateKind                           │
│       ▼                                                                      │
│  pipeline use-case (orchestrates ports only)                                 │
│       ├──► data-collection ports/adapters: YouTube captions, DeepSeek LLM    │
│       └──► supabase-integration writers: materials draft + shortlist enqueue │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Hard boundary (locked):** `ingestion-service` → Supabase only. No import of `backend.interface.http`, no HTTP client to FastAPI, no `web/` knowledge.

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `data-collection` | Ports + DTOs + **external** adapters (YouTube, DeepSeek/Foundry later) | `typing.Protocol` + Pydantic DTOs + adapter classes |
| `ingestion-service` | Thin CLI runner + **its own** composition root + pipeline orchestration | `python -m ingestion_service …`; no HTTP app |
| `supabase-integration` | DB client factory + **ingestion writers** (+ existing reader/admin adapters) | `create_service_role_client`; insert/upsert helpers |
| `backend` | Unchanged for v1.1 writers; continues to **read** drafts via admin shortlist | Existing `get_admin_shortlist` / `/admin/digest` |
| `web` | Unchanged; admin UI already shows `material_status=draft` | `AdminDigestPage` |

### New vs Modified (explicit)

| Artifact | Status | Notes |
|----------|--------|-------|
| `ingestion-service/` package | **NEW** | Workspace member; CLI entry + composition + pipeline |
| `data-collection` DTOs: `Transcript`, `VideoMetadata`, `MaterialDraft`, `TemplateKind` | **NEW / expand** | Prefer additive DTOs; keep `YoutubeSourceDto` / `ArticleAssistDto` as related shapes |
| `data-collection` ports: `TranscriptProvider`, `ArticleGenerator` | **NEW** | Protocols owned here (not in `backend.application.ports`) |
| `data-collection` adapters: YouTube captions, DeepSeek | **NEW** | External SDKs live here — **not** in CLI |
| Prompt templates `lecture.md`, `podcast.md` | **NEW** | Prefer under `data-collection` next to LLM adapter (swap-friendly) |
| `supabase-integration` draft/shortlist enqueue writers | **NEW** | Do not overload backend-coupled `MaterialRepository.save` for identity inserts |
| `supabase-integration` `create_service_role_client` | **Reuse** | Same factory as `backend.composition.live` |
| Schema `materials`, `digest_shortlist_*`, `ingestion_sources`, `source_texts` | **Reuse** | Migrations 001 + 005/006 already sufficient for MVP |
| `backend` ports/use-cases/HTTP | **Unchanged** | Admin triage/publish remain the only path to `ready` + send |
| `web/` | **Unchanged** | UAT proves visibility via existing admin page |
| Migration 005/006 claim RPC | **Unchanged** | Publish path only; ingestion must not call `claim_and_publish_digest` |

## Recommended Project Structure

```
Digital_CDS/
├── data-collection/                         # EXPAND — contracts + external adapters
│   ├── pyproject.toml                       # add youtube-transcript-api, openai (deps of adapters)
│   └── src/data_collection/
│       ├── __init__.py                      # public exports: DTOs + port protocols
│       ├── dto/
│       │   ├── youtube.py                   # existing YoutubeSourceDto (+ VideoMetadata if split)
│       │   ├── transcript.py                # NEW Transcript (captions-only payload)
│       │   ├── material_draft.py            # NEW MaterialDraft (title/dek/body/slug/…)
│       │   ├── template_kind.py             # NEW TemplateKind = lecture | podcast
│       │   └── foundry.py                   # keep ArticleAssistDto for later Foundry swap
│       ├── ports/
│       │   ├── transcript_provider.py       # Protocol: fetch(video_ref) -> Transcript
│       │   └── article_generator.py         # Protocol: generate(transcript, kind) -> MaterialDraft
│       ├── adapters/
│       │   ├── youtube_captions.py          # youtube-transcript-api → Transcript
│       │   └── deepseek_article.py          # OpenAI SDK base_url → MaterialDraft
│       └── prompts/
│           ├── lecture.md
│           └── podcast.md
│
├── ingestion-service/                       # NEW — thin CLI deployable
│   ├── pyproject.toml                       # depends: data-collection, supabase-integration
│   └── src/ingestion_service/
│       ├── __init__.py
│       ├── __main__.py                      # python -m ingestion_service
│       ├── cli.py                           # parse URL, --template, env
│       ├── composition.py                   # OWN wiring (not backend composition)
│       └── pipeline/
│           └── ingest_youtube.py            # orchestrate ports → writers; no SDKs
│
├── supabase-integration/                    # MODIFY — add writers; reuse client
│   └── src/supabase_integration/
│       ├── client.py                        # REUSE create_service_role_client
│       ├── material_repository.py           # EXISTING (backend.domain; reader/admin)
│       ├── shortlist_repository.py          # EXISTING (admin triage/claim)
│       ├── ingestion_source_writer.py       # NEW optional: upsert ingestion_sources (+ source_texts)
│       ├── draft_material_writer.py         # NEW: insert materials status=draft
│       └── shortlist_enqueue_writer.py      # NEW: ensure unsent batch + insert item
│
├── backend/                                 # UNCHANGED for v1.1 write path
├── web/                                     # UNCHANGED
└── pyproject.toml                           # ADD ingestion-service to uv workspace members
```

### Structure Rationale

- **`data-collection` owns adapters:** Matches architecture rule (“adapters of external APIs live in `data-collection`”) and locked decision that this module holds ports/DTOs **and** implementations that belong there. CLI stays thin.
- **`ingestion-service` is composition + orchestration only:** Inbound adapter = CLI. No YouTube/DeepSeek/Supabase SDK imports in pipeline modules — only ports + writer interfaces.
- **Writers stay in `supabase-integration`:** Same module owns schema + PostgREST access; avoids a second Supabase client home. Prefer **ingestion-specific writers** that speak `data-collection` DTOs rather than extending `SupabaseMaterialRepository.save` (which upserts with explicit `id` and maps `backend.domain.Material`).
- **Do not put adapters in CLI “for speed”:** Violates Ports & Adapters and blocks FoundryModels swap (ADR-0002 revisit).
- **Own composition root is intentional:** Architecture rule “wiring only in `backend/.../composition/`” applies to the **HTTP app**. A second deployable must wire itself; it must **not** call into backend composition.

### Recommended package split (decisive)

| Concern | Package | Why |
|---------|---------|-----|
| DTOs + ports | `data-collection` | Locked; public package API |
| YouTube captions adapter | `data-collection` | External API adapter |
| DeepSeek / future Foundry adapter | `data-collection` | Swap LLM behind same port |
| Prompt markdown assets | `data-collection/prompts` | Versioned with generator |
| CLI + env + exit codes | `ingestion-service` | Thin runner |
| Pipeline orchestration | `ingestion-service` | Use-case without FastAPI |
| `create_service_role_client` | `supabase-integration` | Already exists |
| Insert draft + enqueue shortlist | `supabase-integration` | Schema ownership |
| Admin read / approve / send | `backend` + existing adapters | Unchanged |

## Architectural Patterns

### Pattern 1: Dual-hexagon, shared database

**What:** Two processes (FastAPI reader/admin + CLI writer) each with ports/adapters, sharing Postgres tables as the integration contract.  
**When to use:** Write path must not couple to HTTP/auth/SPA; operator-driven one-shot jobs.  
**Trade-offs:** Pros — clear deployables, no FastAPI dependency for operators, RLS bypass isolated to service_role. Cons — no shared transactional saga across HTTP; consistency is “eventual via rows”; duplicate client wiring.

**Example:**
```python
# ingestion_service/pipeline/ingest_youtube.py — ports only
def ingest_youtube_url(
    *,
    url: str,
    template: TemplateKind,
    transcripts: TranscriptProvider,
    articles: ArticleGenerator,
    drafts: DraftMaterialWriter,
    shortlist: ShortlistEnqueueWriter,
) -> MaterialDraft:
    transcript = transcripts.fetch(url)
    draft = articles.generate(transcript, template)
    material_id = drafts.insert_draft(draft)
    shortlist.enqueue(material_id)
    return draft
```

### Pattern 2: Captions-only transcript port (no Whisper)

**What:** `TranscriptProvider` returns text + language + provenance (`model_id="youtube-captions"`, video_id). No audio download.  
**When to use:** v1.1 MVP locked to `youtube-transcript-api`.  
**Trade-offs:** Pros — simple, no media storage (content contract). Cons — fails when captions disabled; cloud egress may hit `RequestBlocked` [MEDIUM — Context7 docs].

```python
class TranscriptProvider(Protocol):
    def fetch(self, video_url_or_id: str, *, languages: tuple[str, ...] = ("ru", "en")) -> Transcript: ...
```

### Pattern 3: LLM behind `ArticleGenerator` with OpenAI-compatible client

**What:** DeepSeek via `OpenAI(api_key=…, base_url=…)` + `chat.completions.create` [MEDIUM — Context7 openai-python + DeepSeek API docs]. Templates select system/user prompt files.  
**When to use:** MVP LLM; later replace adapter with FoundryModels without changing pipeline.  
**Trade-offs:** Pros — one port, ADR-0002 bend is localized. Cons — foreign API temporarily; document revisit.

### Pattern 4: Idempotent source row + draft insert

**What:** Upsert `ingestion_sources` on `(source_system, external_id)` before insert material; link `materials.source_id`. Optionally store captions in `source_texts` (pipeline artifact, **not** published material).  
**When to use:** Re-runs of the same YouTube URL.  
**Trade-offs:** Pros — safe UAT retries. Cons — need a clear policy: skip vs overwrite draft body on re-ingest (recommend: update draft if still `draft` and not approved on shortlist; else fail loudly).

## Data Flow

### Request Flow (v1.1 one-shot)

```
Operator CLI
    ↓  URL + TemplateKind
ingestion-service composition (service_role + DeepSeek key + prompts)
    ↓
TranscriptProvider (YouTube captions)     → Transcript DTO
    ↓
ArticleGenerator (DeepSeek + template)    → MaterialDraft DTO
    ↓
DraftMaterialWriter                       → INSERT materials (status=draft)
    ↓
ShortlistEnqueueWriter                    → ensure unsent batch + INSERT digest_shortlist_items
    ↓
(stop — no publish, no mail, no knowledge index)
```

### Downstream read path (already shipped — no code change)

```
Admin opens /admin/digest
    ↓
backend get_admin_shortlist → ShortlistRepository.get_current_batch
    ↓
items include material_status=draft (same as Phase 5 seed `phase5-admin-draft`)
    ↓
Admin approve → still draft allowed (D-85); send blocked until ready (ADMIN-03)
```

### Key Data Flows

1. **Ingest → draft row:** Prepared markdown only lands in `materials`; never store video/audio blobs as material (D-CONTENT-01).
2. **Ingest → shortlist:** New item `decision=pending`, next `rank`, `score`/`score_factors` nullable or honest placeholders — **do not** fake PIPE-01 ranking honesty labels.
3. **Admin → ready → send:** Existing path only (`publish_material` / editorial promote + `claim_and_publish_digest`). Ingestion never sets `status=ready` or `sent_at`.
4. **No FastAPI coupling:** Integration test for UAT is “rows visible via admin API/UI”, not “CLI called backend”.

### State / status machine touchpoints

```
[external video] --captions--> [Transcript] --LLM--> [MaterialDraft]
                                      |
                                      v
                         materials.status = draft ──(admin/editorial)──► ready ──(send)──► issue
                                      |
                                      v
                         digest_shortlist_items.decision = pending ──► approved|rejected
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Operator, 3–5 videos (v1.1 UAT) | Single CLI process; sequential calls; no queue |
| Tens/week | Same CLI; optional batch argv later — still no HTTP |
| Hundreds / scheduled | New milestone: job runner + `ingestion_jobs` stages; still no reader coupling |
| 100k+ readers | Irrelevant to ingestion; reader path stays FastAPI + RLS |

### Scaling Priorities

1. **First bottleneck:** YouTube IP blocks / missing captions — fail with mapped errors; do not silently invent transcript.
2. **Second bottleneck:** LLM latency/cost — keep one-shot sync CLI; add async jobs only in a later milestone.

## Anti-Patterns

### Anti-Pattern 1: CLI calling FastAPI to “create material”

**What people do:** `POST /admin/...` from the CLI with a service token.  
**Why it's wrong:** Couples ingestion to HTTP/auth surface; violates locked “writes Supabase only”; breaks when API is down but DB is up.  
**Do this instead:** service_role writers in `supabase-integration`.

### Anti-Pattern 2: Adapters inside `ingestion-service`

**What people do:** Put `youtube_transcript_api` / `openai` imports in the CLI package.  
**Why it's wrong:** Makes CLI a god-package; FoundryModels swap rewrites the runner; contradicts module ownership.  
**Do this instead:** Adapters in `data-collection`; CLI wires ports in `composition.py`.

### Anti-Pattern 3: Reusing `SupabaseMaterialRepository.save` for creates

**What people do:** Build a `backend.domain.Material` with a fake `id` and upsert.  
**Why it's wrong:** Identity PK expects omit-on-insert; pulls ingestion into backend domain types; blurs reader port with writer semantics.  
**Do this instead:** `DraftMaterialWriter.insert(draft: MaterialDraft) -> int` using `.insert(...).execute()` without `id`.

### Anti-Pattern 4: Auto-ready or auto-send from ingestion

**What people do:** Set `status=ready` or call claim RPC after LLM.  
**Why it's wrong:** Breaks editorial trust; send-pool draft rules (ADMIN-03) exist for a reason.  
**Do this instead:** Always `draft` + `pending` shortlist; humans triage in `/admin/digest`.

### Anti-Pattern 5: Storing raw transcript as published material body

**What people do:** Dump captions into `body_markdown`.  
**Why it's wrong:** Content contract — material is agent-prepared article only.  
**Do this instead:** LLM markdown → `materials`; optional captions → `source_texts` only.

### Anti-Pattern 6: Extending backend `ShortlistRepository` with enqueue for CLI

**What people do:** Add `enqueue` to the backend port and import it from ingestion.  
**Why it's wrong:** Forces `ingestion-service` → `backend` dependency; mixes admin triage contract with pipeline writes.  
**Do this instead:** Separate `ShortlistEnqueueWriter` protocol (defined next to ingestion or in `data-collection` ports) implemented in `supabase-integration`.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| YouTube captions | Outbound adapter in `data-collection` via `youtube-transcript-api` | `fetch(video_id)`; languages e.g. `ru,en`; map `TranscriptsDisabled` / `NoTranscriptFound` / `RequestBlocked` at boundary [MEDIUM] |
| DeepSeek | Outbound adapter via OpenAI Python SDK `base_url` + API key | Official OpenAI-compatible API; model id from env; ADR-0002 temporary bend [MEDIUM] |
| Supabase PostgREST | `create_service_role_client` | Bypasses RLS; never ship key to `web/` |
| FoundryModels | Deferred adapter behind same `ArticleGenerator` / future transcript port | Not v1.1 |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `ingestion-service` ↔ `data-collection` | Package import (public API) | DTOs + ports + adapters |
| `ingestion-service` ↔ `supabase-integration` | Package import (writers + client) | No deep-import into backend |
| `ingestion-service` ↔ `backend` | **None** | Locked |
| `ingestion-service` ↔ `web` | **None** | Locked |
| Shared DB ↔ `backend` admin | Existing ports | Observes new draft rows |
| Publish path | Unchanged RPC 005/006 | Ingestion must not invoke |

### Schema touchpoints (no new migration expected for MVP)

| Table | Ingestion write | Reader/admin effect |
|-------|-----------------|---------------------|
| `ingestion_sources` | Upsert by `(source_system, external_id)` recommended | Provenance / idempotency |
| `source_texts` | Optional captions store | Not exposed as material |
| `materials` | `INSERT` `status=draft`, `format=статья`, provenance_label set | Appears when joined from shortlist |
| `digest_shortlist_batches` | Ensure one `sent_at IS NULL` for current `week_start` | `get_current_batch` |
| `digest_shortlist_items` | Insert `pending` + next rank | Visible on `/admin/digest` |

### Suggested build order (dependency-aware)

1. **Contracts first (data-collection)** — DTOs (`Transcript`, `VideoMetadata`, `MaterialDraft`, `TemplateKind`) + ports; unit tests with fakes.  
2. **YouTube captions adapter** — red/green against port; error mapping.  
3. **DeepSeek article adapter + templates** — red/green; no DB yet.  
4. **Supabase writers** — `DraftMaterialWriter` + `ShortlistEnqueueWriter` (+ optional source upsert); integration tests marked integration; use service_role.  
5. **ingestion-service composition + CLI** — wire ports; one-shot happy path with fakes, then live smoke.  
6. **UAT** — 3–5 real URLs; confirm drafts in `/admin/digest` via existing backend/UI (no backend changes).  
7. **Defer** — Whisper/Foundry, scheduler, HTTP ingestion API, auto-ready, knowledge indexing on ingest.

**Phase ordering rationale:** Ports before adapters; adapters before writers; writers before CLI composition; UAT last against the already-shipped admin read path so frontend/backend stay untouched.

**Research flags for later phases:**
- Cloud egress / YouTube IP blocking for VM runs (proxy policy).  
- Re-ingest policy when shortlist item already approved.  
- Whether `source_texts` retention is required for audit vs captions-as-ephemeral.

## Sources

- Live codebase: `data-collection/` DTOs; `supabase-integration` material/shortlist repos + `client.py`; migrations `001`, `005`, `006`; `backend` admin shortlist use-case; `.cursor/rules/architecture.mdc`; `.planning/PROJECT.md` v1.1 locks  
- Context7: `/jdepoix/youtube-transcript-api` (fetch/languages/errors) — confidence MEDIUM  
- Context7: `/openai/openai-python` (custom `base_url`) — confidence MEDIUM  
- Context7: `/supabase/supabase-py` (insert + service key client) — confidence MEDIUM  
- DeepSeek API docs (`api-docs.deepseek.com`) — OpenAI-compatible client pattern — confidence MEDIUM  
- Hexagonal CLI-vs-API worker pattern (Thoughtworks / ports-and-adapters literature via Tavily) — confidence LOW alone; **elevated by project architecture rules + existing dual-module layout** → treat dual-hexagon recommendation as HIGH for this repo

---
*Architecture research for: Digest CDS v1.1 YouTube → LLM → Supabase ingestion*  
*Researched: 2026-09-24*
