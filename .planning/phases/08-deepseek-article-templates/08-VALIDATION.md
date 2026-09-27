---
phase: 8
slug: deepseek-article-templates
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-27
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Commands sourced from `08-RESEARCH.md` Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | root `pyproject.toml` — `testpaths = ["tests/unit"]`; `integration` marker already registered |
| **Quick run command** | `uv run pytest tests/unit/test_deepseek_article_adapter.py tests/unit/test_article_error_mapping.py tests/unit/test_article_templates.py tests/unit/test_ingestion_settings.py -x` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run the new unit file(s) with `-x`
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd-verify-work`:** Full suite must be green. No live DeepSeek call required
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-draft | TBD | TBD | LLM-01 | T-08-INPUT | Mocked JSON object → `ArticleDraft`; extra keys ignored; provenance not read from JSON | unit | `uv run pytest tests/unit/test_deepseek_article_adapter.py tests/unit/test_assemble_material_draft.py -x` | ❌ W0 | ⬜ pending |
| 08-templates | TBD | TBD | LLM-02 | — | `lecture` / `podcast` headings in package markdown; missing file raises before any client call | unit | `uv run pytest tests/unit/test_article_templates.py tests/unit/test_deepseek_article_adapter.py -x` | ❌ W0 | ⬜ pending |
| 08-fail | TBD | TBD | LLM-03 | T-08-LEAK | Network, 429, 5xx, 401/403, fences, non-object JSON, blank field → `ArticleError`; message has no transcript or body | unit | `uv run pytest tests/unit/test_deepseek_article_adapter.py tests/unit/test_article_error_mapping.py -x` | ❌ W0 | ⬜ pending |
| 08-honesty | TBD | TBD | LLM-04 | T-08-INJECT | System prompt: transcript-only, always Russian; `ru` format-only; `en` translate; preserve terms; exact suffix ` · пер. с англ.` | unit | `uv run pytest tests/unit/test_deepseek_article_adapter.py tests/unit/test_translation_marker.py -x` | ❌ W0 | ⬜ pending |
| 08-budget | TBD | TBD | LLM-05 | T-08-CAP | `len == 80000` calls SDK; `80001` does not; context is only `char_count` + `max_chars` | unit | `uv run pytest tests/unit/test_deepseek_article_adapter.py tests/unit/test_article_error_mapping.py tests/unit/test_ingestion_settings.py -x` | ❌ W0 | ⬜ pending |
| 08-public | TBD | TBD | D-17 | T-08-KEY | Adapter modules do not read `os.environ`; new adapter and `ArticleError` stay off the package root `__all__` | unit | `uv run pytest tests/unit/test_data_collection_public_api.py -x` | ✅ extend | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

LLM-02 Typer `--template` and LLM-03 live zero-row persist proof are Phase 10 and Phase 9. They are not gates for this phase.

---

## Wave 0 Requirements

- [ ] RED tests for `MAX_TRANSCRIPT_CHARS` default, blank, and invalid values without breaking `from_env({})`
- [ ] RED tests for template headings and missing-file load
- [ ] RED tests for mocked happy path, prompt rules, `ru`/`en` language passthrough, preserved tokens
- [ ] RED tests for D-13 failures, fence rejection, budget boundary, SDK not called when over cap
- [ ] RED tests for `map_article_error` allowlists and message redaction (`message` and `to_dict()`, not only `context`)
- [ ] RED test for the exact English suffix constant ` · пер. с англ.`
- [ ] RED test for additive `FakeArticleGenerator` failures
- [ ] `uv add --package data-collection "openai>=3.0,<4"` then `uv sync` (when tests first import `openai`)
- [ ] Extend runbook §1 with `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`, `MAX_TRANSCRIPT_CHARS` (names and defaults only)
- [ ] Extend `NEGATIVE_ROOT_NAMES` with the new adapter and `ArticleError`
- [ ] Assert this phase adds no Typer app, no Supabase writer, no migration, no `IngestError` stage

*Existing infrastructure: pytest + `tests/unit/` covers Phase 6 ports and Phase 7 adapters — extend, do not replace.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live DeepSeek draft quality (headings, Russian, honesty) | LLM-04 | Needs a key and a human reader | Phase 10 UAT, including one English source video |
| Real HTTP 400 body shape for context length | LLM-05 | Docs page did not yield a stable code sample | Optional integration; unit test stubs `status_code` and `code` |
| Wheel contains `lecture.md` / `podcast.md` | LLM-02 | Packaging | Check if a wheel is built; source-tree tests are the gate |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
