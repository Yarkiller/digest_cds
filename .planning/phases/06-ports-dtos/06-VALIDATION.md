---
phase: 6
slug: ports-dtos
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-26
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (workspace `tests/unit`) |
| **Config file** | root `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `uv run pytest tests/unit/test_transcript_dto.py tests/unit/test_assemble_material_draft.py tests/unit/test_material_draft_type_boundary.py -x` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run targeted new unit file(s) with `-x`
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | DTO-01 | T-06-01 | Reject blank/whitespace Transcript fields | unit | `uv run pytest tests/unit/test_transcript_dto.py -x` | ❌ W0 | ⬜ pending |
| 06-01-02 | 01 | 1 | DTO-01 | T-06-01 | VideoMetadata author/url/id required; published_at optional | unit | `uv run pytest tests/unit/test_video_metadata_dto.py -x` | ❌ W0 | ⬜ pending |
| 06-01-03 | 01 | 1 | DTO-01 | T-06-01 | MaterialDraft required provenance fields; None published_at OK | unit | `uv run pytest tests/unit/test_material_draft_dto.py -x` | ❌ W0 | ⬜ pending |
| 06-01-04 | 01 | 1 | DTO-01 | — | TemplateKind only lecture\|podcast | unit | `uv run pytest tests/unit/test_template_kind.py -x` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 1 | DTO-02 | T-06-03 | FakeTranscriptProvider scripted + `.calls` | unit async | `uv run pytest tests/unit/test_transcript_provider_fake.py -x` | ❌ W0 | ⬜ pending |
| 06-02-02 | 02 | 1 | DTO-02 | T-06-03 | FakeArticleGenerator scripted + `.calls` | unit async | `uv run pytest tests/unit/test_article_generator_fake.py -x` | ❌ W0 | ⬜ pending |
| 06-03-01 | 03 | 2 | D-07 | T-06-04 | Assembler maps fields; does not invent provenance_label | unit | `uv run pytest tests/unit/test_assemble_material_draft.py -x` | ❌ W0 | ⬜ pending |
| 06-03-02 | 03 | 2 | SC-3 | T-06-02 | Transcript rejected where MaterialDraft required | unit | `uv run pytest tests/unit/test_material_draft_type_boundary.py -x` | ❌ W0 | ⬜ pending |
| 06-04-01 | 04 | 2 | D-01…D-04 | T-06-03 | Old DTOs gone; public `__all__` = new surface only; fakes/ArticleDraft not exported | unit / import | `uv run pytest tests/unit/test_data_collection_public_api.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New unit test stubs listed in Per-Task Verification Map (all ❌ today)
- [ ] Delete old DTO modules/tests only after RED tests for the new surface exist (TDD)
- [ ] Confirm async fake tests via `asyncio.run` without adding a pytest-asyncio package if avoidable
- [ ] Assert no diffs under `supabase-integration/migrations/` or `query_embedder.py` for this phase

*Existing pytest + uv workspace infrastructure covers the runner; Wave 0 is new test/product files only.*

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
