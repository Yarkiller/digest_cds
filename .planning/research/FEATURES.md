# Feature Research

**Domain:** YouTube → LLM → CMS draft ingestion (editorial digest CLI MVP)
**Project:** Digest CDS v1.1
**Researched:** 2026-09-24
**Confidence:** MEDIUM (HIGH on brownfield admin/materials contracts; MEDIUM on ecosystem norms)

## Feature Landscape

Scope is **only NEW v1.1 ingestion**: operator CLI one-shot that turns a YouTube URL into a `materials` draft + `digest_shortlist_items` row. Existing v1 features (auth, issue/archive, voting, knowledge, razbory, admin shortlist → preview → send) are **consumers**, not rebuild targets.

### Typical pipeline (ecosystem → Digest CDS)

Industry YouTube→article flows are **transcript-first**: URL → captions → cleanup → LLM restructure → **human editorial gate** → publish. RAG pipelines stop at chunk/embed; editorial products add a CMS draft status so AI output never reaches readers until a person signs off. Generation is the easy ~20%; review is the hard ~80% (HITL CMS patterns).

**Digest CDS mapping (recommended):**

```text
Operator CLI
  → parse YouTube URL → video_id
  → youtube-transcript-api captions (ru/en priority; fail closed if none)
  → DeepSeek (OpenAI-compatible SDK) + template (lecture|podcast)
  → MaterialDraft {title, dek, body_markdown, tags?, roles?}
  → Supabase: ingestion_sources (+ optional source_texts) + materials(status=draft)
  → enqueue digest_shortlist_items on current unsent batch (decision=pending)
  → Admin at /admin/digest: see draft badge → edit/promote ready → Approve → Preview → Send
```

Backend/SPA stay **read/triage** paths; CLI owns fetch + LLM + write. Matches PROJECT.md and D-CONTENT-01 (prepared article only).

### Expected operator behavior (v1.1)

| Step | Operator does | System does | Success signal |
|------|---------------|-------------|----------------|
| 1 | Picks 1 real YouTube URL with captions; chooses `--template lecture\|podcast` | Validates URL → `video_id` | Clear argv/help |
| 2 | Runs one CLI command (env has DeepSeek + Supabase service_role) | Captions → LLM → draft + shortlist enqueue | Non-zero exit on failure; stdout prints `material_id`, `slug`, `batch_id`, `rank` |
| 3 | Opens `/admin/digest` | Row visible with **draft** badge, `decision=pending` | UAT: 3–5 videos appear |
| 4 | (Existing) Promotes material to `ready`, Approve, Preview, Send | `send_digest` still blocks approved∩draft (ADMIN-03 / D-85) | Issue only after human promotion |

Operator does **not** expect: scheduler, HTTP ingest API, Whisper fallback, auto-`ready`, auto-send, or SPA YAML config in this milestone.

### Table Stakes (Users Expect These)

Features the **ingestion operator + admin** assume for this scoped CLI MVP. Missing = pipeline feels broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **CLI one-shot: URL → draft** | Ecosystem CLIs (YouTube→Markdown) are single-command; Digest CDS adds CMS write | MEDIUM | `ingestion-service/` runner; no HTTP. Args: URL, `--template`, optional `--batch`/`--week-start`. |
| **Captions fetch (no Whisper)** | Captions-only MVP; fail if disabled/missing | LOW–MEDIUM | `youtube-transcript-api`: `video_id` not URL; language list `["ru","en"]`; map `TranscriptsDisabled` / `NoTranscriptFound` / `IpBlocked` → operator-visible exit. |
| **LLM → prepared article fields** | Material = article, not raw transcript (D-CONTENT-01) | MEDIUM | Align with existing `ArticleAssistDto` shape: `title`, `dek`, `body_markdown`, `format=статья`, `model_id`, `prompt_version`. DeepSeek via OpenAI SDK `base_url`. |
| **Two templates: lecture + podcast** | Spoken genres differ (structure, tone, sectioning) | LOW–MEDIUM | Files `lecture.md` / `podcast.md`; `TemplateKind` enum in `data-collection` DTOs. |
| **Write `materials` as `status=draft`** | HITL: AI never publishes; admin already shows draft badges | MEDIUM | Reuse schema from `001_initial_schema.sql`. Never set `ready` in CLI. |
| **Enqueue current shortlist batch** | Admin triage is the review UI; empty pipeline = empty shortlist | MEDIUM | Insert `digest_shortlist_items` (`decision=pending`, next `rank`, honest `score_factors`). Target unsent batch (`sent_at IS NULL`). Depends on Phase 5 tables + migration 005 delivery columns (read-only for CLI). |
| **Appear in `/admin/digest`** | UAT acceptance criterion | LOW (integration) | No SPA changes if write contract matches shortlist join on `materials.status`. |
| **Provenance + source identity** | Editorial trust; re-runs must not invent fake sources | MEDIUM | Prefer `ingestion_sources` unique `(source_system, external_id)` + `materials.source_id` + `provenance_label` (YouTube title/channel). Transient captions may land in `source_texts` (not published body). |
| **Idempotent re-run on same video** | Operators re-run after prompt tweaks; duplicates break ≤5 shortlist | MEDIUM | Upsert by `youtube` + `video_id`; update draft body or refuse with clear message; do not duplicate shortlist rows for same `material_id` in batch. |
| **Loud, staged failures** | Caption/LLM/DB failures are common; silent empty drafts erode trust | LOW–MEDIUM | Exit codes + stage labels (`captions` / `llm` / `persist` / `enqueue`). No silent empty `body_markdown`. |
| **Ports/DTOs in `data-collection`** | Architecture rule; Foundry revisit later | LOW | Expand: `Transcript`, `VideoMetadata`, `MaterialDraft`, `TemplateKind`. Keep LLM SDK out of domain. |

### Differentiators (Competitive Advantage)

Not generic YouTube→Markdown; valuable for **Digest CDS editorial contour**.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Draft + shortlist handoff into existing admin HITL** | Differentiator vs file-only CLIs: machine writes into the same approve/preview/send loop already shipped | MEDIUM | Approve-on-draft allowed (D-85); send still blocks draft — CLI must not weaken that gate. |
| **Content contract enforced at write** | Raw video/transcript never become material content | LOW | Body = LLM markdown only; captions stay in ingestion tables or discarded after job. |
| **СВА-oriented templates (lecture/podcast)** | Domain voice vs generic “blog from video” tools | MEDIUM | Prompt versions pinned; Russian editorial tone per CONTEXT. |
| **CLI isolated from backend read path** | Swap DeepSeek→FoundryModels later without SPA churn | LOW–MEDIUM | ADR-0002 bend documented; adapter seam only. |
| **Honest shortlist scoring stubs** | Admin honesty (ADMIN-05): ≥ factors when claiming pipeline scores | LOW | Prefer empty/`{}` or labeled “ingestion-cli” factors — do not fake ranking like PIPE-01. |
| **UAT on 3–5 real videos** | Proves captions+LLM+DB against live YouTube quirks | MEDIUM (ops) | Select videos with captions; document failures (age-restrict, IP block) in runbook. |

### Anti-Features (Commonly Requested, Often Problematic)

Aligned with PROJECT.md **OUT** for v1.1 — do not build.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Ingestion HTTP API** | “So SPA/other services can trigger” | Auth surface, ops coupling, out of milestone | CLI + service_role env; API later |
| **Scheduler / batch playlist ingest** | “Run overnight on a channel” | IP blocks, quota, partial failures, no HITL pacing | Manual 3–5 one-shots for UAT |
| **Whisper / FoundryModels transcription** | Videos without captions | Contour/cost; ADR-0002 revisit; scope blow-up | Fail closed; pick captioned videos |
| **Auto-publish / auto-`ready` / auto-send** | “Fully automated digest” | Violates editorial trust; breaks ADMIN-03 draft block | Always `draft` + pending shortlist |
| **Store/publish raw transcript as material** | Faster demo | Breaks D-CONTENT-01; readers see unedited speech | LLM article only |
| **Admin YAML pipeline UI (PIPE-01)** | Visual config | Deferred post-v1; honesty rules say UI silent on seed vs pipeline | Templates as repo files |
| **Live SMTP / signup mailer** | Close delivery | Separate debt (`g-01-3b`); not ingestion | StubMailer unchanged |
| **Leaderboard / quiz cards** | Engagement | ADR-0001 / deferred | Out of scope |
| **Embedding/knowledge index on ingest** | “Searchable immediately” | Drafts must not leak to readers/search as published knowledge | Index on promote/`ready` (existing publish path) |
| **Silent Whisper fallback on missing captions** | Convenience | Hides OUT-scope ASR; unpredictable cost/latency | Explicit error; operator picks another URL |
| **CLI sets `decision=approved`** | Skip triage | Rubber-stamp risk; bypasses admin accountability | Always `pending` |

## Feature Dependencies

```
data-collection DTOs (Transcript, VideoMetadata, MaterialDraft, TemplateKind)
    └──requires──> YoutubeSourceDto / ArticleAssistDto shapes (brownfield)

Captions adapter (youtube-transcript-api)
    └──requires──> VideoMetadata / video_id parse

DeepSeek LLM adapter + lecture/podcast templates
    └──requires──> Transcript + TemplateKind
    └──produces──> MaterialDraft

Persist materials(status=draft) + ingestion_sources
    └──requires──> MaterialDraft + Supabase service_role
    └──requires──> existing materials schema (001)

Enqueue digest_shortlist_items
    └──requires──> materials.id
    └──requires──> unsent digest_shortlist_batches (Phase 5 / 005)
    └──enhances──> /admin/digest triage (no SPA change)

Admin promote ready → Approve → Preview → Send
    └──requires──> draft row visible
    └──conflicts──> auto-ready / auto-send (anti-features)

Whisper / HTTP API / scheduler / PIPE-01 YAML
    └──conflicts──> v1.1 CLI MVP scope
```

### Dependency Notes

- **MaterialDraft requires captions + template:** No draft without non-blank transcript text and a chosen `TemplateKind`.
- **Shortlist enqueue requires materials row:** FK `digest_shortlist_items.material_id` → `materials`; cannot enqueue orphan scores.
- **Enqueue depends on unsent batch:** If no `sent_at IS NULL` batch, CLI must create one (ops policy) or fail with instructions — decide in phase research; do not attach to sent batches.
- **≤5 shortlist capacity:** Phase 5 contract is ≤5 items; enqueue must handle full batch (reject or replace policy — phase decision).
- **Admin send depends on `ready`:** CLI drafts intentionally cannot send until human promotion — this is a feature, not a bug (ADMIN-03 / D-85).
- **Knowledge search must not index drafts as published:** Keep indexing on existing ready/publish path; do not add chunk+embed in v1.1 CLI.
- **FoundryModels `TranscriptResultDto` / `ArticleAssistDto`:** Reuse field ideas; DeepSeek MVP does not call Foundry — adapters stay swappable.

## MVP Definition

### Launch With (v1.1)

Minimum to validate operator → draft → admin visibility.

- [ ] **CLI one-shot** — URL + `--template lecture|podcast` → exit 0 with ids printed
- [ ] **Captions via `youtube-transcript-api`** — fail closed with stage error
- [ ] **DeepSeek article generation** — `title` / `dek` / `body_markdown`; `prompt_version` recorded
- [ ] **`materials` draft persist** — `status=draft`, provenance, optional `source_id`
- [ ] **Shortlist enqueue** — pending item on current unsent batch
- [ ] **UAT: 3–5 real videos** visible as drafts in `/admin/digest`
- [ ] **`data-collection` ports/DTOs** — Transcript, VideoMetadata, MaterialDraft, TemplateKind

### Add After Validation (v1.1.x / next)

- [ ] **Idempotent upsert UX polish** — `--force` regenerate vs refuse — after first UAT collisions
- [ ] **Richer `ingestion_jobs` stage audit** — if ops need history beyond CLI logs
- [ ] **FoundryModels LLM swap** — when ADR-0002 revisit lands (same MaterialDraft port)
- [ ] **Batch/playlist ingest** — only after single-URL reliability proven

### Future Consideration (v2+)

- [ ] Ingestion HTTP API + auth
- [ ] Scheduler / channel watch
- [ ] Whisper / FoundryModels ASR for caption-less videos
- [ ] PIPE-01 YAML ranking UI
- [ ] Auto-promote policies (still gated)
- [ ] Live SMTP, leaderboard, quiz

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| CLI one-shot URL→draft+enqueue | HIGH | MEDIUM | P1 |
| Captions fetch + loud failures | HIGH | LOW–MEDIUM | P1 |
| DeepSeek + lecture/podcast templates | HIGH | MEDIUM | P1 |
| materials `draft` write + provenance | HIGH | MEDIUM | P1 |
| Shortlist enqueue → `/admin/digest` | HIGH | MEDIUM | P1 |
| data-collection DTOs/ports | HIGH | LOW | P1 |
| Idempotent same-video re-run | MEDIUM | MEDIUM | P1 |
| ingestion_jobs stage rows | MEDIUM | LOW–MEDIUM | P2 |
| Playlist/batch CLI | MEDIUM | HIGH | P3 |
| Whisper fallback | MEDIUM | HIGH | P3 (anti this milestone) |
| HTTP ingest API | LOW (now) | HIGH | P3 |
| Auto-ready / auto-send | LOW (harmful) | LOW | Anti |
| PIPE-01 YAML UI | LOW (now) | HIGH | P3 / OUT |
| Knowledge embed on ingest | LOW (now) | MEDIUM | Anti until ready |

**Priority key:**
- P1: Must have for v1.1 launch / UAT
- P2: Should have when single-URL path is green
- P3: Nice / deferred / OUT this milestone

## Competitor / Analog Feature Analysis

| Feature | File-only YT→MD CLIs | Transcript RAG pipelines | Editorial AI CMS (HITL) | Digest CDS v1.1 |
|---------|----------------------|--------------------------|-------------------------|-----------------|
| Captions fetch | Yes | Yes | Optional | **Yes (only ASR)** |
| LLM article | Often | Query-time only | Yes | **Yes (templates)** |
| CMS draft status | No (files) | No | Yes | **Yes (`materials.draft`)** |
| Human approve before audience | Manual | N/A | Yes | **Yes (existing admin)** |
| Shortlist / digest batch | No | No | Rare | **Yes (enqueue)** |
| Auto-publish | Sometimes | N/A | Discouraged | **No** |
| Scheduler / API | Sometimes | Common | Common | **No (CLI only)** |

## Brownfield dependency checklist (requirements scoping)

Use these categories when writing REQUIREMENTS:

| Category | Depends on (already shipped) | v1.1 must not break |
|----------|------------------------------|---------------------|
| Draft material write | `materials` enum `draft\|ready`, slug unique, `provenance_label` | Reader paths ignore drafts |
| Shortlist enqueue | `digest_shortlist_batches/items`, ≤5, `decision=pending` | Sent batches; rank honesty |
| Admin visibility | `/admin/digest` join `materials.status` | Draft badge semantics |
| Send gate | `send_digest` → `DraftInSendPoolError` | Never auto-`ready` |
| Content contract | D-CONTENT-01; format `статья` | No media-as-material |
| Ingestion identity | `ingestion_sources (source_system, external_id)` | Idempotent YouTube ids |

## Sources

- Project: `.planning/PROJECT.md` (v1.1 goal, OUT list, DeepSeek bend)
- Schema: `supabase-integration/migrations/001_initial_schema.sql` (ingestion + materials + shortlist)
- Admin shortlist: `005_phase5_admin_shortlist.sql`; `send_digest` / D-85 draft block
- DTOs: `data-collection/.../dto/foundry.py` (`ArticleAssistDto`), `youtube.py` (`YoutubeSourceDto`)
- Context7: `/jdepoix/youtube-transcript-api` (fetch/list/errors) — confidence MEDIUM
- Context7: `/openai/openai-python` (custom `base_url` for compatible providers) — confidence MEDIUM
- Tavily web: transcript-first YT→blog workflows; HITL CMS draft gates (llmcms.org, GrowthX) — confidence MEDIUM (verified cross-check with brownfield)
- Tavily web: CLI YT→Markdown analogs (file output only) — confidence MEDIUM

---
*Feature research for: Digest CDS v1.1 YouTube → LLM → Supabase CLI ingestion*
*Researched: 2026-09-24*
