# Pitfalls Research

**Domain:** Digest CDS — YouTube captions → LLM (DeepSeek) → Supabase materials draft + shortlist enqueue (v1.1 ingestion CLI)
**Researched:** 2026-09-24
**Confidence:** HIGH for Digest CDS integration (schema/use-cases read directly); MEDIUM for external YouTube/DeepSeek failure modes (Context7 + Tavily verified)

## Critical Pitfalls

### Pitfall 1: Violating the content contract (media / raw transcript as material)

**What goes wrong:**
Pipeline writes YouTube URL, audio reference, or raw caption text into `materials.body_markdown` (or treats `source_texts.text` as the published article). Reader APIs and issue pages then surface non-editorial content as if it were a prepared article.

**Why it happens:**
Ingestion tables (`ingestion_sources`, `source_texts`) already exist next to `materials`; it is easy to “save everything we fetched” into the publication row. Fast demos also paste the transcript when the LLM call fails.

**How to avoid:**
- Material body = LLM markdown article only; captions stay in transient pipeline memory and/or `source_texts` (ingestion layer), never as material content.
- Require `format = 'статья'` and non-empty prepared `body_markdown` before insert.
- Provenance via `provenance_label` + `source_id` FK — not by embedding the video into the article body.
- Unit tests that reject fixtures where body equals transcript or contains media URLs as primary content.

**Warning signs:**
Admin draft body looks like timed captions; slug/title match video title with no editorial rewrite; `source_texts` empty while `materials.body_markdown` is a dump of segments.

**Phase to address:**
Contracts / DTO phase (before any Supabase write) — lock `MaterialDraft` vs `Transcript` types so they cannot be confused at the type boundary.

---

### Pitfall 2: Writing `status=ready` or auto-publishing / skipping shortlist

**What goes wrong:**
Ingestion sets `materials.status = 'ready'` (or stamps `published_at`), or skips `digest_shortlist_items`. Drafts either appear in reader APIs (`materials_select_ready` / knowledge search only `ready`) without editorial review, or never show in `/admin/digest` because admin UX reads the current shortlist batch, not “all drafts”.

**Why it happens:**
“Make it visible in UAT” pressure; confusing “visible to admin” with “ready for readers”; forgetting that send/preview publish path is `approved ∩ ready` only (`send_digest`, `claim_and_publish_digest`).

**How to avoid:**
- Hard-code ingest write path: `status='draft'`, `published_at=NULL`, always enqueue shortlist row with `decision='pending'`.
- Never call claim/publish/send from CLI.
- Assert in integration tests: after ingest, material is `draft`; shortlist row exists on current unsent batch; GET issue/material reader APIs still omit it.

**Warning signs:**
UAT “works” on knowledge search without admin approve; send pool suddenly non-empty after CLI run; drafts missing from admin shortlist but present in `materials` table.

**Phase to address:**
Supabase draft + shortlist write phase — acceptance criteria: draft+enqueue only; no reader leakage.

---

### Pitfall 3: Wrong batch / rank / silent top-5 truncation

**What goes wrong:**
CLI creates a new `digest_shortlist_batches` row, attaches to an already-`sent_at` batch, or inserts ranks >5 / colliding ranks. Admin `get_current_batch` selects latest `sent_at IS NULL`; `visible_shortlist_items` keeps only top **5** by rank. Extra items exist in DB but never appear in admin UX (deferred v1 issue: post-send-hide-shortlist already showed shortlist visibility is fragile).

**Why it happens:**
Seed migration creates batches by `week_start`; developers copy seed SQL; no product rule for “current batch” in CLI; unlimited append feels fine until UAT.

**How to avoid:**
- Resolve batch exactly like `SupabaseShortlistRepository.get_current_batch`: `sent_at IS NULL`, order `week_start DESC, created_at DESC`, limit 1.
- If none exists, create one unsent batch for the operator’s week — do not attach to sent batches.
- Assign next free `rank` within 1..5; if batch already has 5 items, fail loudly (or documented overflow policy) — never silent insert at rank 6+.
- Unique awareness: PK `(batch_id, material_id)` prevents double material in one batch but does **not** cap count.

**Warning signs:**
SQL shows 7 shortlist rows, admin shows 5; UAT video “ingested” but absent from `/admin/digest`; items land on last week’s sent batch.

**Phase to address:**
Shortlist enqueue phase (same as write phase or immediately after) — batch resolution + capacity tests first.

---

### Pitfall 4: Non-idempotent retries → duplicate materials / orphan rows

**What goes wrong:**
Operator re-runs CLI after LLM timeout or 429. Second run inserts a second `materials` row (new slug) and/or second shortlist line; or inserts material then fails before shortlist → orphan draft invisible in admin; or upserts source but appends duplicate shortlist.

**Why it happens:**
LLM retries are necessary (DeepSeek dynamic 429) but DB writes are not keyed; slug derived from title drifts; `ingestion_sources` unique `(source_system, external_id)` is unused by the writer.

**How to avoid:**
- Natural key: YouTube `video_id` → `ingestion_sources (source_system='youtube', external_id=video_id)` upsert first.
- Deterministic material `slug` from video_id (e.g. `yt-{video_id}`); `ON CONFLICT (slug)` update draft body only when still `draft` and not approved for send.
- Shortlist: `ON CONFLICT (batch_id, material_id) DO NOTHING` (or update rank policy explicitly).
- Prefer single transaction (or ordered saga with compensating delete) for material + shortlist insert.
- Retries of LLM allowed; re-insert of publication rows must be upsert.

**Warning signs:**
Same video twice in shortlist under different material ids; `ingestion_sources` empty while materials pile up; “unique violation” only on second run with different slug.

**Phase to address:**
Idempotency / duplicate-video phase — before UAT of 3–5 videos; include intentional re-run tests.

---

### Pitfall 5: Captions-missing or IP-block treated as transcription opportunity

**What goes wrong:**
`TranscriptsDisabled` / `NoTranscriptFound` / `RequestBlocked` / `IpBlocked` are mishandled: silent empty transcript → garbage LLM article; or engineer adds Whisper/FoundryModels “just for this video,” violating milestone captions-only + ADR-0002 temporary DeepSeek bend scope.

**Why it happens:**
Library error names are misleading (`TranscriptsDisabled` often appears when cloud IP is blocked). Cloud.ru VM IPs match the PyPI warning about cloud provider blocks. Desire to “make UAT pass” overrides fail-closed policy.

**How to avoid:**
- Map all `CouldNotRetrieveTranscript` subclasses to a typed domain failure; CLI exits non-zero; **no** DB write.
- Distinguish ops failure (`RequestBlocked`/`IpBlocked`/`PoTokenRequired`) from content failure (`NoTranscriptFound`/`TranscriptsDisabled` after confirming video has no captions in browser) in logs — same product outcome (fail), different runbook.
- Do not implement Whisper/FoundryModels transcription in v1.1; document ADR-0002 bend (DeepSeek only) with revisit note.
- Smoke one known-caption video from the deploy host before UAT batch.

**Warning signs:**
Works on laptop, fails on VM with `TranscriptsDisabled`; empty transcript length 0 still calls DeepSeek; new Whisper dependency appears in lockfile.

**Phase to address:**
Caption retrieval phase — fail-closed tests before LLM phase.

---

### Pitfall 6: Wrong Supabase key / RLS illusion

**What goes wrong:**
CLI uses anon/publishable or user JWT. Inserts appear to “fail open” (empty data / RLS denial) or engineer disables RLS. Conversely, service_role key is copied into `web/` or committed to `.env` examples that ship to the SPA, bypassing all policies.

**Why it happens:**
Backend already uses service_role for reads; frontend uses publishable key; README says pipeline writes need service_role — easy to wire the wrong client in a new `ingestion-service`.

**How to avoid:**
- Ingestion CLI: `create_service_role_client` only; refuse to start if key missing or looks like anon.
- No new INSERT policies for `authenticated` on materials/shortlist in this milestone.
- Keep service_role out of Vite env (`VITE_*`); mask via existing secrets tooling.
- Test: authenticated client cannot insert draft; service_role can.

**Warning signs:**
PostgREST 401/empty insert with no exception; “fixed” by adding permissive INSERT policy for anon; service_role in browser network tab.

**Phase to address:**
Supabase write / composition wiring phase — key selection tests day one of that phase.

---

### Pitfall 7: LLM output / schema mismatch (`format`, empty body, roles, score_factors)

**What goes wrong:**
DeepSeek returns HTML, JSON wrapper, or empty string; insert violates `format = 'статья'` check; `roles` empty breaks later knowledge filters; `score_factors` left as `{}` without honesty path (admin shows «обоснование недоступно» — OK) or fake factors invented by the CLI.

**Why it happens:**
OpenAI-compatible ≠ identical behavior; no output validation before insert; copying seed JSON with fake score factors.

**How to avoid:**
- Validate/strip LLM output to markdown article; reject empty/too-short body.
- Set `format='статья'` in writer, not from model.
- Minimal honest shortlist: `decision=pending`, `score` null or heuristic documented, `score_factors={}` acceptable (ADMIN-05 honesty already handles empty).
- Pin DeepSeek model id; retry only 429/5xx with backoff — never retry 400 by re-sending the same bad payload in a loop that also writes DB.

**Warning signs:**
Check constraint errors on `format`; drafts with `````json fences as body; admin factor labels look like prompt leakage.

**Phase to address:**
LLM + templates phase, with writer validation shared in write phase.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| DeepSeek instead of FoundryModels (ADR-0002 bend) | Ship captions→article MVP fast | Contour / compliance revisit; adapter swap later | v1.1 only if bend documented + FoundryModels revisit tracked |
| Persist full transcript in `source_texts` | Debug / re-run without YouTube | Retention & content-contract risk if UI ever links it | OK if never exposed as material; purge policy TBD |
| Non-transactional material then shortlist | Simpler first adapter | Orphan drafts; partial UAT failures | Never for happy path — use txn or compensating delete |
| Silent skip when shortlist full (>5) | CLI “succeeds” | Operator thinks video is in admin triage | Never — fail or explicit `--force-new-batch` later |
| Blind LLM retry without upsert | Survives 429 | Duplicate materials | Never |
| Adding Whisper “just for missing captions” | Higher UAT pass rate | Scope/ADR breach; media pipeline complexity | Never in v1.1 |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| YouTube captions (`youtube-transcript-api`) | Treat any exception as “no captions” → empty string | Fail closed; log exception class; no LLM/DB on failure |
| YouTube on Cloud.ru VM | Assume laptop success ⇒ VM success | Expect `IpBlocked`/`RequestBlocked`; verify from deploy host |
| DeepSeek (OpenAI SDK) | Retry all errors; unbounded retries | Backoff on 429/5xx only; pin model; timeout; no DB write until success |
| Supabase `materials` | Insert as `ready` for “visibility” | Always `draft`; admin visibility via shortlist |
| Supabase `digest_shortlist_*` | Insert without resolving current unsent batch | Mirror `get_current_batch`; cap ranks ≤5 |
| Supabase RLS | Use anon key “like the SPA” | service_role for CLI writer only |
| `claim_and_publish_digest` | Call from ingestion to “finish the job” | Never — admin send path only; approved∩ready |
| Reader APIs / knowledge search | Embed drafts into `knowledge_chunks` early | Defer embeddings until editorial marks `ready` (out of v1.1 scope) |
| Ports & Adapters | `ingestion-service` imports Supabase SDK deep into “domain” | DTOs in `data-collection`; writer adapter in supabase-integration or thin CLI composition |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Sequential caption+LLM with no timeout | CLI hangs 30+ min under DeepSeek load | Explicit HTTP timeouts (tens of seconds); max retry budget | First flaky network UAT |
| Re-fetching captions on every LLM retry | Extra YouTube calls → faster IP block | Cache transcript in memory for the run; upsert source once | Cloud IP block mid-batch |
| Embedding / chunking on every draft ingest | Slow CLI; vector index churn | Do not write `knowledge_chunks` in v1.1 | Already painful at tens of drafts |
| Unbounded shortlist growth | Admin still shows 5; DB bloat | Cap / fail at 5 per current batch | Operator runs 20 URLs “for UAT” |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| service_role in frontend or committed secrets | Full RLS bypass; data wipe/exfil | CLI-only env; never `VITE_`; secret scanner |
| Prompt injection from video title/captions into SQL/shell | Unexpected queries / path writes | Parameterized Supabase client only; no shell interpolation of transcript |
| Storing DeepSeek key in repo | Key theft; cost abuse | Env / mask store only |
| Opening INSERT policies on materials for `authenticated` | Employees insert/publish via PostgREST | Keep writes service_role-only; no new open write policies |
| Logging full captions + API keys | Leakage in shared VM logs | Redact secrets; truncate transcript in logs |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Draft never appears on `/admin/digest` | Admin thinks pipeline broken | Always enqueue current batch; UAT checks admin UI not only SQL |
| Draft approved while still `draft` then Send | Send blocked (`DraftInSendPoolError`) — confusing if CLI set wrong expectations | CLI/docs: “draft for triage; mark ready in editorial path before send” |
| Duplicate videos in shortlist | Cluttered triage; wrong approve | Idempotent upsert by video_id |
| Opaque CLI failure (“error”) on missing captions | Operator retries forever | Russian/clear exit: captions unavailable vs IP blocked vs LLM down |
| Success message without shortlist confirmation | False confidence | Print material id, batch id, rank, status=draft |

## "Looks Done But Isn't" Checklist

- [ ] **Content contract:** Body is prepared markdown, not captions/URL dump — verify sample row
- [ ] **Status:** `materials.status = draft` and `published_at IS NULL` — verify SQL
- [ ] **Shortlist:** Row on **current unsent** batch with `rank` ∈ 1..5 — verify `/admin/digest`
- [ ] **Idempotency:** Second CLI run for same URL does not create a second material — verify unique video_id
- [ ] **Captions fail-closed:** Video without captions exits non-zero with **zero** new materials — verify
- [ ] **RLS key:** Writer uses service_role; anon cannot insert — verify
- [ ] **No auto-publish:** CLI never sets `ready` / never calls claim_and_publish — verify code + test
- [ ] **ADR-0002 bend:** DeepSeek documented as temporary; no Whisper added — verify PROJECT/ADR note
- [ ] **TDD:** Failing tests existed before writer/LLM adapters — verify git history / RED evidence
- [ ] **Format check:** `format = 'статья'` — verify constraint-safe insert

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Orphan draft (no shortlist) | LOW | Insert missing shortlist row into current batch or delete draft material |
| Duplicate materials same video | MEDIUM | Keep one draft; delete extras; fix slug/upsert; clean shortlist PK conflicts |
| Drafts inserted as `ready` | HIGH | Set back to `draft`, clear `published_at`; audit whether any issue already referenced them |
| Attached to sent batch | MEDIUM | Move/reinsert items onto new unsent batch; do not unsend published issues lightly |
| IP-blocked caption fetches | MEDIUM | Diagnose from VM; pause batch; do not invent Whisper in-milestone |
| Partial UAT pollution | LOW | Delete test materials by slug prefix + shortlist rows; avoid `RESET` on shared VM |

## Pitfall-to-Phase Mapping

Suggested v1.1 phase order for prevention (names indicative for roadmap):

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Content contract / DTO mix-up | 1 — Ports & DTOs (`Transcript` ≠ `MaterialDraft`) | Type tests; reject transcript-as-body fixtures |
| Captions missing / IP block mishandled | 2 — Caption fetch (fail-closed) | Unit tests per exception class; no DB mock calls on failure |
| LLM garbage / format violations | 3 — DeepSeek + templates | Output validator tests; pinned model; retry policy tests |
| service_role / RLS wrong key | 4 — Supabase writer wiring | Anon insert fails; service_role draft insert passes |
| Always draft + shortlist enqueue | 4 — Draft + enqueue | status=draft; row on current batch; admin GET shows item |
| Wrong batch / rank >5 truncation | 4 — Draft + enqueue | Capacity test at 5; sent batch rejected |
| Non-idempotent duplicates | 5 — Duplicate video / re-run hardening | Re-run same URL → single material + single shortlist row |
| Auto-publish / ready creep | 5 — Hardening + UAT | CLI cannot set ready; reader APIs omit drafts |
| ADR-0002 bend forgotten | Docs gate in phase 3 or milestone close | PROJECT/ADR note + no Whisper dependency |

## Sources

- Digest CDS schema & RLS: `supabase-integration/migrations/001_initial_schema.sql` (materials draft/ready; ingestion unique keys; shortlist PK; `materials_select_ready`)
- Admin publish rules: `005_phase5_admin_shortlist.sql` / `006_claim_publish_material_ids.sql` — `approved ∩ ready` only; service_role RPC
- Admin visibility & send guards: `backend/.../shortlist_repository.py` (`get_current_batch`), `domain/shortlist.py` (`MAX_SHORTLIST_ITEMS=5`), `send_digest.py` (`DraftInSendPoolError`)
- Adapter contract: `supabase-integration/README.md` — pipeline writes via service_role
- Milestone constraints: `.planning/PROJECT.md` v1.1 (captions-only, DeepSeek bend, draft+shortlist, no backend/SPA write path)
- ADR-0002: `docs/adr/0002-cloud-ru-foundrymodels-deployment.md` (FoundryModels intended; media not stored as material)
- youtube-transcript-api errors: Context7 `/jdepoix/youtube-transcript-api` + PyPI cloud IP block warning [confidence: MEDIUM]
- DeepSeek OpenAI-compatible retries/429: Tavily web digests [confidence: MEDIUM]
- Supabase service_role bypasses RLS: Context7 `/websites/supabase` [confidence: MEDIUM]
- ETL idempotency / upsert: Tavily web digests [confidence: MEDIUM]
- Deferred: `post-send-hide-shortlist` (STATE.md) — shortlist visibility already a known fragility

---
*Pitfalls research for: Digest CDS YouTube → LLM → Supabase ingestion (v1.1)*
*Researched: 2026-09-24*
