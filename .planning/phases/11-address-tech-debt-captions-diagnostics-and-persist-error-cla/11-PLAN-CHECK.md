---
status: issues_found
type: plan-check
phase: 11-address-tech-debt-captions-diagnostics-and-persist-error-cla
checked: 2026-10-02
mode: standard
iteration: 1
verdict: VERIFICATION FAILED
blockers: 1
warnings: 2
info: 1
---

# Phase 11 Plan Check — Captions diagnostics & persist error classification

**Phase goal:** Secret-safe captions/URL diagnostics; out-of-catalog SDK → `unknown_captions_error`; persist `23514` + numeric HTTP without changing `PERSIST_REASONS`; sent-batch re-run `already_saved: true` via migration 009
**Plans checked:** `11-01-PLAN.md` · `11-02-PLAN.md` · `11-03-PLAN.md` · `11-04-PLAN.md`
**Requirements:** CAP-02, PERS-02, CLI-02, CLI-04
**Do not replan from this file** — this is a revision-gate report.

## ISSUES FOUND

**Phase:** 11-address-tech-debt-captions-diagnostics-and-persist-error-cla
**Plans checked:** 4
**Issues:** 1 blocker(s), 2 warning(s), 1 info

### Blockers — these properties must hold

**1. [research_resolution] RESEARCH.md carries no unresolved open question**
- Plan: null (phase-level)
- Evidence: `11-RESEARCH.md` has `## Open Questions` without `(RESOLVED)` suffix; Q1 (Studio apply timing) and Q2 (bare Exception wrap) lack inline `RESOLVED` markers. Plans already answer both (11-03 decision + 11-04 apply; 11-01 discretion / RED-only catch), but Dimension 11 requires RESEARCH markers before execution.
- Example fix (non-binding): Mark `## Open Questions (RESOLVED)` and add `RESOLVED:` lines citing the plan dispositions.

### Warnings — these properties should hold

**1. [requirement_coverage] Phase goal URL-envelope secrecy has an explicit lock or freeze assertion**
- Plan: 11-01
- Evidence: ROADMAP goal names “captions/URL envelopes never leak SDK text”; D-02 freezes URL allowlists, but no task asserts URL mapper redaction / allowlist freeze (only captions path + “do not expand” prose). Accidental URL allowlist drift would not fail a planned test.
- Example fix (non-binding): Add a minimal URL allowlist/redaction freeze assertion in an existing captions/CLI suite, or cite an existing green URL test by name in plan 01 acceptance criteria.

**2. [task_completeness] Frontmatter `files_modified` matches task `<files>` for mutable production paths**
- Plan: 11-01
- Task: 2
- Evidence: Task 2 `<files>` includes `ingestion-service/src/ingestion_service/mapping/captions.py`, but plan frontmatter `files_modified` omits it. Wave-overlap / scope accounting can miss optional mapper edits.
- Example fix (non-binding): Add `mapping/captions.py` to `files_modified`, or drop it from `<files>` if the task is truly lock-tests-only with no production edit path.

### Advisories (info)

**1. [task_completeness] Task type is one of `auto` | `tdd` | `checkpoint:*`**
- Plan: 11-01
- Task: 1
- Evidence: Task 1 uses `type="tracer"` (structure validator accepted it; fields complete). Nonstandard vs documented type set.
- Example fix (non-binding): Use `type="auto" tdd="true"` or `type="tdd"` and keep tracer intent in the task name/objective.

### Structured Issues

```yaml
issues:
  - plan: null
    dimension: research_resolution
    severity: blocker
    required_property: "RESEARCH.md carries no unresolved open question"
    description: "11-RESEARCH.md ## Open Questions lacks (RESOLVED) suffix; Q1 Studio apply timing and Q2 bare Exception wrap have Recommendations but no inline RESOLVED markers"
    fix_hint: "Rename to ## Open Questions (RESOLVED) and mark each question RESOLVED with the plan disposition (11-03/11-04 apply split; RED-only catch discretion)"

  - plan: "11-01"
    dimension: requirement_coverage
    severity: warning
    required_property: "Phase goal URL-envelope secrecy has an explicit lock or freeze assertion"
    description: "Goal and D-02 cover URL envelopes/allowlists, but no task names a URL redaction/allowlist freeze test; only captions CliRunner/mapper locks are planned"
    task: 2
    fix_hint: "Assert URL allowlist freeze or cite existing URL redaction test in 11-01 acceptance criteria"

  - plan: "11-01"
    dimension: task_completeness
    severity: warning
    required_property: "Frontmatter files_modified matches task <files> for mutable production paths"
    description: "Task 2 lists mapping/captions.py in <files> but files_modified omits it"
    task: 2
    fix_hint: "Sync files_modified with task <files> or remove captions.py from <files> if lock-only"

  - plan: "11-01"
    dimension: task_completeness
    severity: info
    required_property: "Task type is one of auto | tdd | checkpoint:*"
    description: "Task 1 type=\"tracer\" is nonstandard though fields are complete and verify.plan-structure valid=true"
    task: 1
    fix_hint: "Prefer type=auto tdd=true (or type=tdd) with tracer in the name"
```

### Recommendation

1 blocker, 2 warning(s) require revision. Returning to planner with feedback.

---

## Dimension results (goal-backward)

### Coverage Summary

| Requirement | Plans | Status |
|-------------|-------|--------|
| CAP-02 | 01 | Covered (D-01…D-05) |
| PERS-02 | 02 | Covered (D-06/D-07 classification only; enqueue logic untouched) |
| CLI-02 | 03, 04 | Covered (009 + fake invert + blocking apply) |
| CLI-04 | 04 | Covered (sent-batch checkmarks CliRunner) |

### Decision coverage (D-01…D-09)

| Decision | Plans / tasks | Status |
|----------|---------------|--------|
| D-01 message/allowlisted context | 11-01 T1–T2 | Covered |
| D-02 no allowlist expand | 11-01 T1–T2 | Covered (captions); URL freeze weak → warning |
| D-03 no log/debug | 11-01 T1–T2 | Covered |
| D-04 unknown_captions_error | 11-01 T1 | Covered |
| D-05 no Traceback | 11-01 T1 | Covered |
| D-06 23514 + int HTTP → rpc_error | 11-02 T1–T2 | Covered |
| D-07 PERSIST_REASONS frozen | 11-02 T1–T2 | Covered |
| D-08 already_saved sent-batch | 11-03 T2–T3, 11-04 T1 | Covered |
| D-09 RPC amend via 009 | 11-03 checkpoint + T2, 11-04 apply | Covered |

Deferred ideas (`--debug`, structlog, Phase 6 DTO, WR-03/WR-04 unless blocking, etc.): not present in plans → PASS.

### Plan Summary

| Plan | Tasks | Files (frontmatter) | Wave | depends_on | Structure | Estimate | Status |
|------|-------|---------------------|------|------------|-----------|----------|--------|
| 01 | 2 | 4 | 1 | [] | valid | 20k / under budget | Issues (W/I) |
| 02 | 2 | 2 | 1 | [] | valid | 17.5k / under budget | Valid |
| 03 | 3 | 4 | 1 | [] | valid | 25k / under budget | Valid |
| 04 | 2 | 1 | 2 | 11-01, 11-03 | valid | 15k / under budget | Valid |

### Dependency / coupling

- Graph acyclic; wave 2 matches deps; no same-wave `files_modified` overlap.
- Threat IDs unique across plans (`T-11-01`…`T-11-08`; `T-11-SC` reserved per plan).
- Undeclared same-wave coupling: none flagged.

### Key links / wiring

| Link | Planned | Status |
|------|---------|--------|
| Adapter/Fake → map_captions_error → CLI stderr JSON | 11-01 | Covered |
| PostgrestAPIError.code → DraftPersist* | 11-02 | Covered |
| sent-batch conflict → jsonb already_saved | 11-03 | Covered |
| Fake already_saved → CLI checkmarks | 11-04 | Covered |
| Offline 009 → live Studio/psql apply | 11-03 → 11-04 blocking | Covered |

### Scope sanity

All plans ≤3 tasks; estimates under smart-zone budget (`confidence: high`, sample_count=11). PASS.

### Verification derivation

must_haves truths are operator-observable (stderr JSON, classification reasons, already_saved, apply gate). PASS.

### Architectural tier compliance (7c)

| Capability | Expected tier | Plan placement | Status |
|------------|---------------|----------------|--------|
| SDK → CaptionsError | data-collection adapter | 11-01 | PASS |
| CaptionsError → IngestError | ingestion mapper | 11-01 | PASS |
| Persist classification | supabase_persist adapter | 11-02 | PASS |
| PERSIST_REASONS freeze | mapper (no mutate) | 11-02 | PASS |
| Sent-batch already_saved | Database RPC + offline SQL tests | 11-03 | PASS |
| CLI checkmarks / apply | CLI unit + human DB gate | 11-04 | PASS |

### Cross-plan data contracts (9)

Sent-batch `already_saved` shape consistent across SQL contract, fake invert, and CLI test. No conflicting transforms. PASS.

### CLAUDE.md compliance (10)

SKIPPED (no `./CLAUDE.md`). AGENTS.md / architecture / TDD: plans require failing tests first, adapter-boundary mapping, no Python video_id pre-check, no new deps. PASS against project rules.

### Pattern compliance (12)

Plans `@`-include `11-PATTERNS.md` and cite analogs (008 migration, `test_phase10_migration_008.py`, `test_check_violation_maps_to_batch_error`, BatchTrackingFakePersister, CLI mid-pipeline JSON stderr). PASS.

## Dimension 8: Nyquist Compliance

| Task | Plan | Wave | Automated Command | Failing Direction | Status |
|------|------|------|-------------------|-------------------|--------|
| Captions CliRunner | 01 | 1 | `uv run pytest tests/unit/test_cli_ingest_contract.py -x` | stated | ✅ |
| Mapper/adapter locks | 01 | 1 | captions + youtube adapter pytest | stated | ✅ |
| 23514 batch | 02 | 1 | persister contract pytest | stated | ✅ |
| int HTTP rpc_error | 02 | 1 | persister contract pytest | stated | ✅ |
| D-09 decision gate | 03 | 1 | `git ls-files -- …/008_…sql` | stated | ✅ |
| Migration 009 SQL | 03 | 1 | `test_phase11_migration_009.py` | stated | ✅ |
| Fake/overflow invert | 03 | 1 | overflow pytest | stated | ✅ |
| CLI sent-batch | 04 | 2 | cli ingest contract pytest | stated | ✅ |
| [BLOCKING] apply 009 | 04 | 2 | `git ls-files -- …/009_…sql` + human-check | stated | ✅ |

Sampling: Wave 1 & 2 — no 3 consecutive tasks without automated verify → ✅  
Wave 0: gaps listed in VALIDATION.md; plans create the missing tests (no `<automated>MISSING</automated>` sentinels) → ✅  
Failing directions: stated on all runnable automations (probe not injected in this spawn; presence verified in PLAN XML) → ✅  
VALIDATION.md exists; `nyquist_compliant: false` expected pre-execution → gate OK  
Overall Dimension 8: ✅ PASS (pending research_resolution fix elsewhere)

## Special gates (requested)

| Gate | Result |
|------|--------|
| Threat models (`<threat_model>`, ASVS L1, block_on=high, high→mitigate) | PASS (4/4) |
| One-way D-09 checkpoint before authoring 009 | PASS (11-03 `checkpoint:decision`) |
| Blocking schema apply before live CLI-02 claim | PASS (11-04 `checkpoint:human-verify` `[BLOCKING]`) |
| TDD task order (failing test first) | PASS (all `tdd="true"` tasks) |
| Decision coverage D-01…D-09 | PASS (URL freeze assertion weak → warning only) |

## VERIFICATION FAILED

**Blockers:**
1. `11-RESEARCH.md` Open Questions not marked RESOLVED (Dimension 11).

Plans otherwise deliver secret-safe captions diagnostics, persist 23514/int→rpc_error without `PERSIST_REASONS` mutation, and sent-batch `already_saved` via migration 009 with the required one-way + blocking apply gates.
