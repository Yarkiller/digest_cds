# Roadmap: Digest CDS

## Milestones

- ✅ **[v1 MVP](milestones/v1-ROADMAP.md)** — Phases 1-5 (shipped 2026-09-22)
- 🚧 **v1.1 YouTube → LLM → Supabase ingestion** — Phases 6-10 (in progress)

## Phases

<details>
<summary>✅ v1 MVP (Phases 1-5) — SHIPPED 2026-09-22</summary>

- [x] Phase 1: Platform Foundation & Auth (8/8 plans) — completed 2026-09-19
- [x] Phase 2: Issue, Materials & Archive (6/6 plans) — completed 2026-09-20
- [x] Phase 3: Voting Cycle (6/6 plans) — completed 2026-09-20
- [x] Phase 4: Knowledge & Razbory (10/10 plans) — completed 2026-09-21
- [x] Phase 5: Admin Digest Publish (9/9 plans) — completed 2026-09-22

Full phase detail: [milestones/v1-ROADMAP.md](milestones/v1-ROADMAP.md)

</details>

### 🚧 v1.1 YouTube → LLM → Supabase ingestion (In Progress)

**Milestone Goal:** Operator can run a CLI one-shot that turns a YouTube URL into a `materials` draft and a shortlist row — without touching backend/SPA read paths.

- [ ] **Phase 6: Ports & DTOs** - Typed Transcript / MaterialDraft boundaries and in-memory port fakes
- [ ] **Phase 7: Captions Adapter** - YouTube URL → captions with fail-closed, zero-row exits
- [ ] **Phase 8: DeepSeek Article & Templates** - Validated MaterialDraft via lecture/podcast templates, honesty and fail-closed LLM errors
- [ ] **Phase 9: Draft Persist & Shortlist Enqueue** - materials draft + provenance + overflow-safe shortlist enqueue
- [ ] **Phase 10: CLI Composition & UAT** - Typer one-shot, idempotency, staged progress, separate env, 3–5 video UAT

## Phase Details

### Phase 6: Ports & DTOs
**Goal**: `data-collection` exposes typed ingestion contracts so adapters and the CLI never mix transcript with prepared article
**Depends on**: Nothing (v1.1 first phase; builds on shipped v1 schema/admin readers)
**Requirements**: DTO-01, DTO-02
**Success Criteria** (what must be TRUE):
  1. Types `Transcript`, `VideoMetadata`, `MaterialDraft`, and `TemplateKind` exist in `data-collection` and pass unit tests
  2. Ports `TranscriptProvider` and `ArticleGenerator` have in-memory fakes that unit tests can inject without network or DB
  3. A `Transcript` cannot be passed where a `MaterialDraft` is required (type boundary holds in tests)
**Plans**: TBD

### Phase 7: Captions Adapter
**Goal**: Operator can resolve a YouTube URL to captions, or get a loud captions-stage failure with no database side effects
**Depends on**: Phase 6
**Requirements**: CAP-01, CAP-02
**Success Criteria** (what must be TRUE):
  1. Given a YouTube URL, the captions path resolves `video_id` and returns a `Transcript` preferring `ru` then `en`
  2. Missing, disabled, or blocked captions exit non-zero with `stage=captions`
  3. A captions failure writes zero database rows (no partial materials or shortlist items)
**Plans**: TBD

### Phase 8: DeepSeek Article & Templates
**Goal**: Operator can turn a transcript into a validated prepared-article draft via lecture or podcast templates, with fail-closed LLM and context-budget behavior
**Depends on**: Phase 7
**Requirements**: LLM-01, LLM-02, LLM-03, LLM-04, LLM-05
**Success Criteria** (what must be TRUE):
  1. DeepSeek (OpenAI-compatible SDK) returns a validated `MaterialDraft` with `title`, `dek`, `body_markdown`, and provenance fields
  2. Operator can choose `--template lecture|podcast` backed by repository markdown templates
  3. Network/5xx/invalid JSON/validation LLM failures exit non-zero with `stage=llm`, zero database rows, and no partial output
  4. System prompt requires honesty (transcript-only facts; output language matches transcript); oversized transcripts fail closed with `stage=llm_truncation` and no silent truncation
**Plans**: TBD

### Phase 9: Draft Persist & Shortlist Enqueue
**Goal**: A successful draft write lands as `status=draft` with required provenance and appears on an unsent shortlist batch (creating a new batch when the current one is full)
**Depends on**: Phase 8
**Requirements**: PERS-01, PERS-02
**Success Criteria** (what must be TRUE):
  1. A successful persist inserts `materials` with `status=draft` only (never `ready`) and required provenance fields `source_url`, `youtube_video_id`, `source_author`, `source_published_at`, `provenance_label` (migration added if live schema lacks columns)
  2. The run enqueues `digest_shortlist_items` on the current unsent batch with `decision=pending`
  3. When the current unsent batch already has 5 items, the run creates a new unsent batch and enqueues there (does not fail-if-full)
  4. Persist/enqueue never attaches to a batch with `sent_at` set
**Plans**: TBD

### Phase 10: CLI Composition & UAT
**Goal**: Operator runs one Typer command end-to-end with staged progress, idempotent re-runs, separate env, and 3–5 real videos visible as drafts in `/admin/digest`
**Depends on**: Phase 9
**Requirements**: CLI-01, CLI-02, CLI-03, CLI-04, CLI-05
**Success Criteria** (what must be TRUE):
  1. `ingestion-service` Typer one-shot prints `material_id`, `slug`, `batch_id`, and `rank` on success
  2. Re-running the same `video_id` does not create duplicate materials or shortlist rows
  3. CLI prints staged progress (`✓ transcript` / `✓ LLM` / `✓ saved`) and loads secrets from `ingestion-service/.env` (not the backend env file)
  4. UAT: 3–5 real captioned videos appear as drafts in `/admin/digest` with no backend/SPA code changes required
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Platform Foundation & Auth | v1 | 8/8 | Complete | 2026-09-19 |
| 2. Issue, Materials & Archive | v1 | 6/6 | Complete | 2026-09-20 |
| 3. Voting Cycle | v1 | 6/6 | Complete | 2026-09-20 |
| 4. Knowledge & Razbory | v1 | 10/10 | Complete | 2026-09-21 |
| 5. Admin Digest Publish | v1 | 9/9 | Complete | 2026-09-22 |
| 6. Ports & DTOs | v1.1 | 0/? | Not started | - |
| 7. Captions Adapter | v1.1 | 0/? | Not started | - |
| 8. DeepSeek Article & Templates | v1.1 | 0/? | Not started | - |
| 9. Draft Persist & Shortlist Enqueue | v1.1 | 0/? | Not started | - |
| 10. CLI Composition & UAT | v1.1 | 0/? | Not started | - |
