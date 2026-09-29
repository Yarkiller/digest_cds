---
phase: "10"
slug: "cli-composition-uat"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-29"
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `10-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest `>=8.3.0` |
| **Config file** | root `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests/unit"]`) |
| **Quick run command** | `uv run pytest tests/unit/test_cli_ingest_contract.py tests/unit/test_ingest_pipeline.py -x` |
| **Full suite command** | `uv run pytest tests/unit -q` |
| **Estimated runtime** | ~60 seconds (targeted); full unit suite longer |

---

## Sampling Rate

- **After every task commit:** Run the task's targeted `uv run pytest … -x` command
- **After every plan wave:** Run `uv run pytest tests/unit -q`
- **Before `/gsd-verify-work`:** Full unit suite must be green, and manual `10-UAT.md` must have four video rows filled
- **Max feedback latency:** 60 seconds for the targeted command

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 10-W0-CLI | TBD | 0 | CLI-01, CLI-04, D-08, D-10 | T-10-SC | Success stdout prints four id lines; checkmarks stop after a failing stage; missing env is human stderr with no JSON `stage`/`ok` keys | unit (CliRunner) | `uv run pytest tests/unit/test_cli_ingest_contract.py -x` | ❌ W0 | ⬜ pending |
| 10-W0-PIPE | TBD | 0 | CONSISTENCY-01 | T-10-SC | Mismatched ids stop at `stage=consistency`; article generator and persist are not called | unit | `uv run pytest tests/unit/test_ingest_pipeline.py -x` | ❌ W0 | ⬜ pending |
| 10-W0-RPC | TBD | 0 | CLI-02 | T-10-SC | Second persist of the same `video_id` returns stored slug and `already_saved: true`; no duplicate material | unit + SQL contract | `uv run pytest tests/unit/test_persist_idempotency_overflow.py tests/unit/test_phase10_migration_008.py -x` | ⚠️ extend / ❌ W0 | ⬜ pending |
| 10-W0-ENV | TBD | 0 | CLI-05 | T-10-SC | `ingestion-service/.env.example` holds the CLI keys; the CLI does not read a dotenv path itself | unit + file assert | `uv run pytest tests/unit/test_ingestion_env_example.py -x` | ❌ W0 | ⬜ pending |
| 10-UAT | TBD | — | CLI-03 | — | Four real drafts visible in `/admin/digest` (lecture/podcast × ru/en) | manual | — | ❌ W0 (`10-UAT.md`) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_cli_ingest_contract.py` — covers CLI-01, CLI-04, D-05…D-11
- [ ] `tests/unit/test_ingest_pipeline.py` — CONSISTENCY-01, provenance suffix, captions-then-metadata order, CAP-02 persist spy through the full pipeline
- [ ] `tests/unit/test_phase10_migration_008.py` — SQL/contract: conflict returns stored slug + `already_saved`
- [ ] `tests/unit/test_ingestion_env_example.py` — CLI-05 example keys present; not the root backend file
- [ ] Replace `test_ingestion_service_has_no_typer_import` with “only `cli.py` imports typer”
- [ ] Extend `FakeDraftPersister` / `PersistResult` / adapter parse tests for `already_saved`
- [ ] `10-UAT.md` manual checklist (four videos) — not automated

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 3–5 real captioned videos appear as drafts in `/admin/digest`, including at least one English source whose draft is Russian | CLI-03 | Live YouTube, DeepSeek, and Supabase service credentials; D-13 forbids Playwright | Fill four rows in `10-UAT.md` (lecture/podcast × ru/en) and confirm drafts in `/admin/digest` with no backend/SPA code changes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s for targeted commands
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
