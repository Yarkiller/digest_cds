# Project Research Summary

**Project:** Digest CDS v1.1 (YouTube → LLM → Supabase CLI ingestion)
**Domain:** Editorial digest CMS — captions-first YouTube → prepared article → HITL draft/shortlist
**Researched:** 2026-09-24
**Confidence:** HIGH

## Executive Summary

Digest CDS v1.1 is a **write-side ingestion MVP**: an operator CLI that turns one YouTube URL into a `materials` row (`status=draft`) plus a `digest_shortlist_items` row on the current unsent batch, so existing `/admin/digest` triage can review it. Experts in this niche build **transcript-first, HITL-gated** pipelines — captions → LLM restructure → CMS draft — never auto-publish. Generation is the easy ~20%; editorial review is the hard ~80%.

**Recommended approach:** Expand `data-collection` (DTOs/ports + YouTube captions + DeepSeek adapters), add a thin `ingestion-service/` Typer CLI with its own composition root, and extend `supabase-integration` with draft/enqueue writers using sync `create_service_role_client`. Backend and SPA stay **unchanged** readers. Stack pins: `youtube-transcript-api` ≥1.2, official `openai` SDK → DeepSeek (`deepseek-flash`), Typer, existing Pydantic/Supabase lock. Dual-hexagon, shared-database architecture: CLI writes Supabase only; no FastAPI/HTTP ingest, no Whisper, no scheduler.

**Key risks:** (1) content-contract slip (raw transcript/media as material), (2) auto-`ready`/skip-shortlist so drafts leak to readers or vanish from admin, (3) wrong/full shortlist batch (silent rank >5), (4) non-idempotent re-runs → duplicates, (5) captions IP-block on Cloud.ru treated as Whisper opportunity. Mitigate with typed `Transcript` ≠ `MaterialDraft`, hard-coded `draft`+`pending` enqueue, batch resolution mirroring `get_current_batch`, upsert by YouTube `video_id`, and fail-closed caption errors with no DB write.

## Key Findings

### Recommended Stack

Brownfield uv workspace: expand `data-collection`, reuse `supabase-integration` service_role, add `ingestion-service` as a new workspace member. Do not re-litigate FastAPI/React/Auth — v1.1 is ingestion-only. Prefer file markdown templates over LangChain; sync PostgREST over async; captions-only over Whisper/`yt-dlp`.

Details: [STACK.md](./STACK.md)

**Core technologies:**
- **Python ≥3.12 + uv workspace** — matches locked backend/supabase-integration runtime
- **`ingestion-service/` (new) + Typer 0.27.x** — thin one-shot CLI composition root; keeps YouTube/LLM out of FastAPI
- **`data-collection` + `youtube-transcript-api` 1.2.x + `openai` 3.x → DeepSeek** — external adapters behind ports; model `deepseek-flash` (env-overridable)
- **`supabase-integration` sync service_role** — insert draft materials + enqueue shortlist; RLS bypass only in CLI env
- **Pydantic v2** — existing DTO standard; additive `Transcript` / `MaterialDraft` / `TemplateKind`

### Expected Features

Scope is **only** the CLI pipeline; auth, voting, knowledge, admin approve→preview→send remain consumers. Table stakes are single-command URL→draft+enqueue with loud staged failures and admin visibility. Differentiators are handoff into the existing HITL loop and СВА-oriented lecture/podcast templates — not file-only Markdown dumpers.

Details: [FEATURES.md](./FEATURES.md)

**Must have (table stakes):**
- CLI one-shot: URL + `--template lecture|podcast` → print `material_id` / batch / rank
- Captions fetch (fail closed; no Whisper)
- DeepSeek → `title` / `dek` / `body_markdown` with `prompt_version`
- Persist `materials` as `status=draft` + provenance
- Enqueue pending item on current unsent shortlist batch
- Appear in `/admin/digest` (UAT: 3–5 real videos)
- Ports/DTOs in `data-collection`; idempotent same-video re-run

**Should have (competitive):**
- Draft + shortlist into existing admin HITL (vs file-only CLIs)
- Content contract enforced at write (LLM article only)
- Honest shortlist `score_factors` stubs (no fake PIPE-01 ranking)
- Adapter seam for later FoundryModels swap (ADR-0002 bend)

**Defer (v2+ / OUT this milestone):**
- Ingestion HTTP API, scheduler/playlist ingest, Whisper/Foundry ASR
- Auto-`ready` / auto-send, PIPE-01 YAML UI, knowledge embed on ingest
- Live SMTP, leaderboard, quiz

### Architecture Approach

Two deployables share Postgres as the integration contract: existing FastAPI reader/admin hexagon and a new CLI write hexagon. `ingestion-service` must not import `backend` or call HTTP; adapters live in `data-collection`; writers live in `supabase-integration`. No new migrations expected for MVP (001 + 005/006 suffice).

Details: [ARCHITECTURE.md](./ARCHITECTURE.md)

**Major components:**
1. **`data-collection`** — DTOs, `TranscriptProvider` / `ArticleGenerator` ports, YouTube + DeepSeek adapters, `lecture.md` / `podcast.md`
2. **`ingestion-service`** — Typer CLI, own `composition.py`, pipeline orchestration (ports only)
3. **`supabase-integration` writers** — `DraftMaterialWriter`, `ShortlistEnqueueWriter`, optional `ingestion_sources` upsert; reuse `create_service_role_client`
4. **`backend` + `web`** — unchanged; admin shortlist already surfaces `draft` badges

### Critical Pitfalls

Details: [PITFALLS.md](./PITFALLS.md)

1. **Content contract violation** — Never put captions/URL/media in `materials.body_markdown`; keep `Transcript` ≠ `MaterialDraft` at the type boundary; require non-empty prepared markdown + `format='статья'`.
2. **Auto-ready / skip shortlist** — Always `draft` + `pending` enqueue; never claim/publish/send from CLI; admin visibility = shortlist, not “all materials.”
3. **Wrong batch / silent rank >5** — Resolve unsent batch like `get_current_batch`; fail loudly at capacity 5; never attach to `sent_at` batches.
4. **Non-idempotent retries** — Upsert `ingestion_sources` by `(youtube, video_id)`; deterministic slug; shortlist `ON CONFLICT DO NOTHING`; no DB write until LLM succeeds.
5. **Captions fail → Whisper creep / empty LLM** — Map transcript exceptions to non-zero exit with zero rows; distinguish IP-block vs no-captions in runbook; smoke from deploy host before UAT.

## Implications for Roadmap

Based on research, suggested phase structure (dependency-aware; mirrors architecture build order + pitfall prevention):

### Phase 1: Ports & DTOs (`data-collection` contracts)
**Rationale:** Everything else depends on typed boundaries; prevents transcript-as-body and backend-domain coupling.
**Delivers:** `Transcript`, `VideoMetadata`, `MaterialDraft`, `TemplateKind`; `TranscriptProvider` / `ArticleGenerator` protocols; unit tests with fakes.
**Addresses:** Ports/DTOs table stake; content-contract lock.
**Avoids:** Pitfall 1 (content contract / DTO mix-up).

### Phase 2: Captions adapter (fail-closed)
**Rationale:** Captions gate the pipeline; fail-closed must be proven before any LLM or DB spend.
**Delivers:** `youtube-transcript-api` 1.2.x adapter; URL→`video_id`; language `ru`/`en`; mapped domain errors; no Whisper.
**Uses:** `youtube-transcript-api` ≥1.2; optional oEmbed via `httpx` for title later.
**Implements:** `TranscriptProvider` adapter in `data-collection`.
**Avoids:** Pitfall 5 (empty transcript / Whisper scope creep).

### Phase 3: DeepSeek article + lecture/podcast templates
**Rationale:** Produce validated `MaterialDraft` before persistence; localize ADR-0002 bend behind the port.
**Delivers:** OpenAI SDK + DeepSeek `base_url`; `lecture.md` / `podcast.md`; output validation (markdown, non-empty body); retry 429/5xx only; document temporary DeepSeek bend.
**Uses:** `openai` 3.x, model `deepseek-flash` (env-overridable).
**Implements:** `ArticleGenerator` adapter + prompt assets.
**Avoids:** Pitfall 7 (garbage LLM / format mismatch); ADR-0002 forgotten.

### Phase 4: Supabase draft + shortlist enqueue writers
**Rationale:** Admin UAT path requires draft row + current-batch item; service_role wiring is a security gate.
**Delivers:** `DraftMaterialWriter.insert` (no fake id); `ShortlistEnqueueWriter` (ensure unsent batch, ranks 1..5, fail if full); composition refuses anon key; integration tests marked.
**Addresses:** materials draft write; shortlist enqueue; appear in `/admin/digest`.
**Avoids:** Pitfalls 2, 3, 6 (ready creep, wrong batch, wrong key).

### Phase 5: CLI composition + idempotency + UAT
**Rationale:** Wire the one-shot only after ports/adapters/writers are green; harden re-runs before 3–5 video UAT.
**Delivers:** `ingestion-service` Typer CLI; staged exit codes (`captions`/`llm`/`persist`/`enqueue`); upsert by `video_id`; stdout ids; UAT 3–5 captioned videos visible as drafts; no backend/SPA changes.
**Addresses:** CLI one-shot; idempotent re-run; UAT acceptance.
**Avoids:** Pitfall 4 (duplicates); auto-publish creep; orphan drafts.

### Phase Ordering Rationale

- Ports before adapters before writers before CLI — matches hexagonal ownership and TDD fakes-first.
- Fail-closed captions before LLM/DB — avoids garbage drafts and wasted API cost.
- Batch capacity + service_role in the write phase — admin visibility and RLS are acceptance blockers.
- Idempotency before multi-video UAT — operators will re-run after prompt tweaks.
- Backend/web untouched last — UAT proves shared-DB integration, not new HTTP surfaces.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (captions):** Cloud.ru / datacenter IP blocking (`IpBlocked` / `PoTokenRequired`); proxy or residential runbook.
- **Phase 4 (enqueue):** Policy when no unsent batch exists (create vs fail); exact behavior at ≤5 capacity; whether `source_texts` retention is required.
- **Phase 5 (idempotency):** Re-ingest when shortlist item already `approved` (update draft vs refuse).

Phases with standard patterns (skip research-phase):
- **Phase 1 (DTOs/ports):** Established repo Ports & Adapters + Pydantic patterns.
- **Phase 3 (DeepSeek via OpenAI SDK):** Official OpenAI-compatible client; pin model + validate output.
- **Phase 4 key wiring:** Existing `create_service_role_client` already used by backend live composition.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Context7 + PyPI pins + repo lockfile; MEDIUM caveat on `openai` 3.x / `httpx2` uv resolve |
| Features | MEDIUM | HIGH on brownfield admin/materials contracts; MEDIUM on ecosystem analogs |
| Architecture | HIGH | Boundaries verified against live codebase + architecture rules; SDK details MEDIUM |
| Pitfalls | HIGH | Schema/use-cases read directly; external YouTube/DeepSeek failure modes MEDIUM |

**Overall confidence:** HIGH

### Gaps to Address

- **uv lock resolve for `openai` 3.x + `httpx2`:** Confirm `uv sync` early in Phase 3; fallback pin `openai` 2.11.x if conflict.
- **Unsent-batch create policy:** Decide in Phase 4 planning — CLI creates week batch vs operator instruction exit.
- **Full-batch overflow:** Fail vs `--force-new-batch` — product decision before enqueue implementation.
- **VM caption smoke:** Validate one known-caption video from Cloud.ru host before UAT batch (Phase 2/5).
- **Re-ingest after shortlist approve:** Explicit refuse/update policy in Phase 5 research.
- **`source_texts` retention:** Optional for MVP; purge/audit policy deferred unless ops demand it.

## Sources

### Primary (HIGH confidence)
- Repo: `data-collection` DTOs; `supabase-integration` client/repos; migrations `001`, `005`, `006`; backend `get_current_batch` / `send_digest`; `.cursor/rules/architecture.mdc`; `.planning/PROJECT.md`
- Context7 `/jdepoix/youtube-transcript-api` — `fetch`, exceptions, cloud IP warning
- Context7 `/openai/openai-python` — custom `base_url`, chat.completions
- Context7 `/websites/api-docs_deepseek` + https://api-docs.deepseek.com/ — DeepSeek models / OpenAI-compatible client
- Context7 `/supabase/supabase-py` — sync client insert patterns
- PyPI (2026-09-24): `youtube-transcript-api==1.2.4`, `openai==3.19.2`, `typer==0.27.2`
- Repo lockfile: `supabase==2.31.0`, `httpx==0.28.1`, `pydantic==2.13.5`
- ADR-0002 FoundryModels deployment (bend + revisit)

### Secondary (MEDIUM confidence)
- Context7 `/fastapi/typer` — CLI patterns
- Tavily: transcript-first YT→blog / HITL CMS draft gates; DeepSeek 429 retry norms; ETL upsert patterns
- Hexagonal CLI-vs-API worker literature (elevated by repo architecture rules)

### Tertiary (LOW confidence)
- Generic competitor feature tables for file-only YT→MD CLIs — directional only; Digest CDS differentiator is CMS handoff

---
*Research completed: 2026-09-24*
*Ready for roadmap: yes*
