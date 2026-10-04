---
phase: 15-cli-debug-diagnostics
verified: 2026-10-04T08:31:05Z
status: gaps_found
score: 11/12 must-haves verified
covered_files:
  - .planning/phases/15-cli-debug-diagnostics/15-01-PLAN.md
  - .planning/phases/15-cli-debug-diagnostics/15-01-SUMMARY.md
  - .planning/phases/15-cli-debug-diagnostics/15-02-PLAN.md
  - .planning/phases/15-cli-debug-diagnostics/15-02-SUMMARY.md
  - ingestion-service/src/ingestion_service/adapters/stderr_diagnostics.py
  - ingestion-service/src/ingestion_service/application/ports/diagnostics.py
  - ingestion-service/src/ingestion_service/application/use_cases/ingest_pipeline.py
  - ingestion-service/src/ingestion_service/cli.py
  - ingestion-service/src/ingestion_service/diagnostics/__init__.py
  - ingestion-service/src/ingestion_service/diagnostics/redaction.py
  - ingestion-service/src/ingestion_service/tests_support/fakes.py
  - tests/unit/test_cli_debug_diagnostics.py
  - tests/unit/test_debug_redaction.py
  - tests/unit/test_ingest_pipeline.py
  - tests/unit/test_stderr_diagnostics.py
covered_digest: "v2:sha256:b0608bcc9ecf47aace8f0a3b4473b4bdc708711473456d81e9bfea70480757e2"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "SC2 / D-07 / D-08: the redaction safety net (`sanitize` + `DENY_PATTERNS`) masks credential-shaped values (cookies, bearer tokens, JWTs, URL userinfo, credential assignments) so no secret/key value, proxy credential, cookie, or auth token can reach an emitted debug line"
    status: failed
    reason: >-
      The assignment DENY_PATTERN relies on `\b…\b` word boundaries, and `_` is a word
      character, so it cannot match underscore-compound credential names. Independently
      reproduced (verifier-run probe): `sanitize("secret_key=abcdef123456")`,
      `sanitize("access_token=abcdef123456")`, `sanitize("client_secret=abcdef123456")`,
      `sanitize("refresh_token=abcdef123456")`, `sanitize("private_key=abcdef123456")`,
      and `sanitize("auth=abcdef123456")` all return the input unchanged (LEAK), while
      `api_key=`/`token=`/`secret=` are masked. Separately, the control-character
      pattern is applied *after* the token patterns, so
      `sanitize("Bearer abc\ndef_secondhalf")` → `'[redacted]def_secondhalf'` (partial
      leak). These are exactly the credential shapes DBG-01/SC2 names (proxy
      credentials, cookies, auth tokens). `tests/unit/test_debug_redaction.py` only
      exercises `secret`/`cookie`/`Bearer`/JWT/userinfo without an underscore suffix,
      so the suite stays green.
    artifacts:
      - path: ingestion-service/src/ingestion_service/diagnostics/redaction.py
        issue: >-
          Assignment DENY_PATTERN at L47-50 uses `\b` boundaries that cannot match
          `access_token`/`secret_key`/`client_secret`/`refresh_token`/`private_key`;
          `_CONTROL_CHARS` is the last element (L51) while `sanitize` applies
          `DENY_PATTERNS` in order (L74-80), so a credential split by a control
          character leaks its tail.
      - path: tests/unit/test_debug_redaction.py
        issue: >-
          Denylist coverage tests `secret`/`cookie`/`Bearer`/JWT/URL-userinfo only, not
          underscore-compound credential names; `test_deny_patterns_is_tuple_of_compiled_patterns`
          asserts container shape, not redaction behavior.
    missing:
      - "Use a non-word boundary (e.g. `(?<![A-Za-z0-9_])`) and/or add `access[_-]?token`, `refresh[_-]?token`, `client[_-]?secret`, `secret[_-]?key`, `private[_-]?key` to the assignment pattern."
      - "Strip control characters before applying the deny token patterns."
      - "Add regression cases (`secret_key=…`, `access_token=…`, `client_secret=…`, control-char-split Bearer) to `tests/unit/test_debug_redaction.py`."
---

# Phase 15: CLI --debug diagnostics Verification Report

**Phase Goal:** Operators can opt into richer ingest diagnostics without secret leakage or regressing default progress
**Verified:** 2026-10-04T08:31:05Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | SC1 / DBG-01: `ingestion-service` CLI accepts `--debug` and prints richer stage diagnostics on stderr | ✓ VERIFIED | `cli.py:79-83` declares `typer.Option("--debug", …)` (explicit flag name, default `False`); `test_debug_success_emits_stage_lines` green; verifier probe emitted 4 `[HH:MM:SS] debug stage=…` lines on stderr |
| 2 | SC1 / D-04: a successful `--debug` run prints exactly one line per stage — captions, metadata, llm, persist — with the D-04 signals | ✓ VERIFIED | `test_debug_success_emits_all_stage_lines` + `test_debug_stage_lines_carry_allowlisted_signals` green; `ingest_pipeline.py` emits start→complete for all four stages |
| 3 | SC1 / D-01: debug is never written to stdout; stdout is byte-identical with and without `--debug` | ✓ VERIFIED | `StderrDiagnostics` emits via injected `emit` (`cli.py:67-69` `typer.echo(..., err=True)`) / injected stream / `sys.stderr` fallback only; `test_debug_success_emits_stage_lines` asserts `result.stdout.splitlines() == EXPECTED_SUCCESS_LINES` while `--debug` is on |
| 4 | SC3 / DBG-02: without `--debug`, stderr is empty and stdout matches the frozen success contract | ✓ VERIFIED | `NullDiagnostics` is a true no-op; `test_debug_off_is_byte_identical` asserts `result.stderr == ""` and the frozen lines; `test_cli_ingest_contract.py` green |
| 5 | SC3 / DBG-02: `IngestError.to_dict()` JSON envelope and exit codes remain unchanged with `--debug` off (and after debug lines when on) | ✓ VERIFIED | `test_cli_ingest_contract.py` (error paths) green; `test_debug_failure_prints_completed_and_failed` parses the last stderr line as the unchanged JSON envelope and asserts the debug lines precede it |
| 6 | SC2 / D-07: only allowlisted signal keys are emitted; full transcript/prompt bodies are never emitted (counts only) | ✓ VERIFIED | `ALLOWED_KEYS` filter in `stderr_diagnostics._emit`; `test_non_allowlisted_keys_are_dropped` green; `ingest_pipeline.py` emits `transcript_chars`/`transcript_words`/`response_chars`, never `transcript.text`/`body_markdown` |
| 7 | SC2 / D-08: exact runtime `Settings` secrets (`deepseek_api_key`, `supabase_secret_key`, `youtube_proxy_url`) are masked before emission | ✓ VERIFIED | `SecretRegistry` masking + `_settings_secrets` wiring (`cli.py:51-60`); `test_secret_registry_masks_exact_value` green; **verifier probe** with `settings.deepseek_api_key == video_id` emitted `video_id=[redacted]` and the sentinel never appeared in stderr |
| 8 | SC2 / D-07 / D-08 / D-09: the redaction safety net masks credential-shaped values (cookies, bearer, JWT, URL userinfo, credential assignments) so none can reach an emitted line | ✗ FAILED | Verifier probe: `sanitize("secret_key=…")`, `"access_token=…"`, `"client_secret=…"`, `"refresh_token=…"`, `"private_key=…"` return input unchanged; `sanitize("Bearer abc\ndef_secondhalf")` → `'[redacted]def_secondhalf'`. See Gaps. |
| 9 | T-F / D-06: the metadata debug line exposes only `video_id` — never the author or the full source URL | ✓ VERIFIED | `test_debug_metadata_line_minimized` asserts the line lacks `"Rick Astley"` and the `source_url` string |
| 10 | T-G / D-10 / D-11: on `IngestError`, completed-stage lines plus the failed stage's `reason`, `exit_code`, and `elapsed_ms` are printed before the JSON envelope; `url`/`consistency` failures report `elapsed_ms=0` | ✓ VERIFIED | `test_debug_failure_prints_completed_and_failed`, `test_debug_url_failure_prints_stage_line_with_zero_elapsed`, `test_captions_failure_records_stage_failed`, `test_article_failure_records_stage_failed_after_completed_stages`, `test_invalid_url_records_stage_failed_without_stage_start` green |
| 11 | T-H / D-12: a pre-video `ConfigurationError`/`TemplateLoadError` prints a `stage=config` line and mints no `IngestError` JSON envelope | ✓ VERIFIED | `test_debug_config_error_line` + `test_debug_template_load_error_line` green; `test_config_error_without_debug_has_no_debug_line` green |
| 12 | T-D: `run_ingest_pipeline` depends only on the `StageDiagnostics` protocol and imports no `time`/`sys`/`typer`/`datetime` | ✓ VERIFIED | `application/ports/diagnostics.py` (Protocol + `NullDiagnostics`, no `Any`); AST guard `test_ingest_pipeline_retains_no_infra_imports` green |

**Score:** 11/12 truths verified (0 present, behavior-unverified; 1 failed)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `ingestion-service/src/ingestion_service/diagnostics/redaction.py` | `ALLOWED_KEYS`, `SecretRegistry`, `DENY_PATTERNS`, `sanitize` | ⚠️ PARTIAL | All symbols exist and allowlist/registry are correct; `DENY_PATTERNS` assignment boundary + control-char ordering are defective (see gap) |
| `ingestion-service/src/ingestion_service/application/ports/diagnostics.py` | `DebugValue`, `Clock`, `StageDiagnostics`, `NullDiagnostics` | ✓ VERIFIED | Protocol + runtime_checkable + no-op; no `Any` at the boundary |
| `ingestion-service/src/ingestion_service/adapters/stderr_diagnostics.py` | `SystemClock`, `StderrDiagnostics` (stderr-only, injected clock/emitter) | ✓ VERIFIED | Framework-free (no `typer`); emits via injected stream/emitter/`sys.stderr` fallback; allowlist filter + `sanitize` applied |
| `ingestion-service/src/ingestion_service/application/use_cases/ingest_pipeline.py` | All stage hooks + `stage_failed` attribution, infra-free | ✓ VERIFIED | Start/complete per stage; `stage_failed` in every mapping block; AST guard green |
| `ingestion-service/src/ingestion_service/cli.py` | `--debug` flag, sink wiring, `_settings_secrets`, `settings` in deps | ✓ VERIFIED | Flag explicit; sink rebuilt with secrets after `build_ingest_deps`; `settings=settings` in namespace |
| `ingestion-service/src/ingestion_service/tests_support/fakes.py` | `FakeClock`, `RecordingDiagnostics` | ✓ VERIFIED | Both present and used by tests |
| `tests/unit/test_cli_debug_diagnostics.py` | CLI on/off, per-stage, metadata, failure, config, AST guard | ✓ VERIFIED | 12 tests, green |
| `tests/unit/test_stderr_diagnostics.py` | Deterministic formatting, control chars, allowlist | ✓ VERIFIED | Exact-line `FakeClock` assertions green |
| `tests/unit/test_debug_redaction.py` | Registry + denylist + mask-not-fail | ⚠️ PARTIAL | Passes, but missing underscore-compound negative cases (let C-1 through) |

**Artifacts:** 9/9 exist; 7 fully substantive, 2 partial (both tied to the redaction gap).

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `cli.main` | `StderrDiagnostics`/`NullDiagnostics` | `debug` flag branch (`cli.py:84-98`) | ✓ WIRED | Sink rebuilt with `_settings_secrets(...)` after deps load |
| `cli.main` | `run_ingest_pipeline` | `diagnostics=diagnostics` (`cli.py:108`) | ✓ WIRED | Optional keyword absorbed by the use-case |
| `run_ingest_pipeline` | `StageDiagnostics` | `stage_started`/`stage_completed`/`stage_failed` guarded by `if diagnostics is not None` | ✓ WIRED | `RecordingDiagnostics` event-order tests green |
| `StderrDiagnostics` | `typer.echo(..., err=True)` | injected `emit` callable (`cli.py:67-69`) | ✓ WIRED | No stdout path; adapter stays `typer`-free |
| `cli` config-error handler | `diagnostics.config_error` → human text | `cli.py:110-114` | ✓ WIRED | `stage=config` line precedes unchanged human text; no JSON envelope |
| `_settings_secrets` | `SecretRegistry` → `sanitize` → stderr | `getattr(deps, "settings", None)` | ✓ WIRED | Verified by verifier probe (`video_id=[redacted]`) |

**Wiring:** 6/6 connections verified.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Phase 15 named suite | `uv run pytest tests/unit/test_cli_debug_diagnostics.py tests/unit/test_stderr_diagnostics.py tests/unit/test_debug_redaction.py tests/unit/test_ingest_pipeline.py tests/unit/test_cli_ingest_contract.py tests/unit/test_ingest_error.py -q` | 47 passed in 2.20s | ✓ PASS |
| Full workspace suite (run once) | `uv run pytest -q` | 711 passed, 1 warning | ✓ PASS |
| Architecture guard (`typer` only in `cli.py`) | `uv run pytest tests/unit/test_data_collection_public_api.py -q` | 27 passed | ✓ PASS |
| Registry wiring end-to-end (`--debug` + `settings.deepseek_api_key == video_id`) | verifier probe (CliRunner) | `video_id=[redacted]`; sentinel absent from stderr; stdout unchanged | ✓ PASS |
| Denylist credential-shape coverage | verifier probe (`sanitize(...)`) | `secret_key=`/`access_token=`/`client_secret=`/`refresh_token=`/`private_key=` unchanged (LEAK); `Bearer abc\ndef_secondhalf` → `[redacted]def_secondhalf` | ✗ FAIL |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| DBG-01 | 15-01, 15-02 | CLI accepts `--debug` and prints richer stage diagnostics without leaking secrets/proxy creds/cookies/full transcript bodies | ✓ SATISFIED (primary path) | `--debug` + per-stage lines verified; allowlist + registry prevent leakage; denylist safety-net hardening tracked as the gap below |
| DBG-02 | 15-01, 15-02 | With `--debug` off, staged progress / `IngestError.to_dict()` contracts unchanged | ✓ SATISFIED | `test_debug_off_is_byte_identical` + `test_cli_ingest_contract.py` green; stderr empty, stdout/exit codes frozen |

No orphaned Phase 15 IDs: both plans declare `requirements: [DBG-01, DBG-02]`, and `REQUIREMENTS.md` maps exactly DBG-01/DBG-02 to Phase 15.

### Prohibitions

| Statement | Verdict | Evidence |
| --------- | ------- | -------- |
| Never print secret/key values, proxy credentials, cookies, or auth tokens | ⚠️ PARTIAL | Allowlist + exact-value registry hold (probe); the denylist enforcement net is broken for underscore-compound credential names (gap) |
| Never print full transcript or prompt bodies — only lengths/counters | ✓ held | `ingest_pipeline.py` emits `transcript_chars`/`transcript_words`/`response_chars`; bodies never passed to the sink |
| Never write debug output to stdout | ✓ held | Sink emits only via `err=True` echo / injected stream; stdout frozen in all `--debug` tests |
| Never fail or abort an ingest because of a redaction violation — mask or omit instead | ✓ held | `sanitize` never raises (`test_sanitize_never_raises_and_masks_on_violation`); `_emit` is unconditional in the use-case |
| Never enable debug via an environment variable; only the `--debug` flag | ✓ held | No env read in `cli.py`; only the `typer.Option("--debug")` branch constructs a live sink |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `ingestion-service/src/ingestion_service/diagnostics/redaction.py` | 47-50 | `\b(?:…secret…token…)\b\s*[=:]` cannot match `_`-suffixed/compound credential names | 🛑 Blocker | DBG-01/SC2 security invariant unenforced for the most common credential shapes |
| `ingestion-service/src/ingestion_service/diagnostics/redaction.py` | 51, 74-80 | Control-char pattern applied last, after token patterns | ⚠️ Warning | A credential split by a control char leaks its tail (partial mask) |
| `tests/unit/test_debug_redaction.py` | 32-35, 39-50 | Presence/shape-only assertions; no underscore-compound negative cases | ⚠️ Warning | Test tier gave false confidence; let the blocker through |
| `ingestion-service/src/ingestion_service/adapters/stderr_diagnostics.py` | 89-95 | Unquoted `key=value` values (Info I-1) | ℹ️ Info | An allowlisted string value containing spaces can render pseudo-fields (`message=foo reason=…`) |
| `ingestion-service/src/ingestion_service/cli.py` | 84-98 | `StderrDiagnostics` constructed twice (Info I-2) | ℹ️ Info | Pre-`build_ingest_deps` sink is intentional (config errors); duplication is easy to misread |
| `ingestion-service/src/ingestion_service/diagnostics/redaction.py` | 36, 81 | `MAX_VALUE_LENGTH` caps the whole line, not each value (Info I-3) | ℹ️ Info | A long `message` truncates mid-value and drops trailing fields |
| `ingestion-service/src/ingestion_service/diagnostics/redaction.py` | 74-80 | `pattern is _CONTROL_CHARS` identity check (Info I-4) | ℹ️ Info | Refactor-fragile; reordering silently changes strip→mask semantics |

**Anti-patterns:** 1 blocker, 2 warnings, 4 info. No `TBD`/`FIXME`/`XXX` debt markers in phase-modified files.

### Human Verification Required

None — all must-have truths were checked programmatically (unit suite, AST guard, and verifier-run behavioral probes). The one failed truth is a code defect with a reproducible probe, not a human-judgment item.

### Gaps Summary

The phase delivers its primary outcome: `--debug` is opt-in, prints one secret-safe line per stage on stderr, and leaves stdout, the JSON error envelope, exit codes, and the no-flag path byte-identical. The allowlist default-emission path and the exact-value `SecretRegistry` (end-to-end via `_settings_secrets`, independently probe-verified) are sound, and failure/config diagnostics are correct.

One goal-level invariant is not met: the phase's own **denylist safety net** (`DENY_PATTERNS` / `sanitize`) does not redact underscore-compound credential names or control-char-split tokens. Independently reproduced:

- `sanitize("secret_key=abcdef123456")` → unchanged (LEAK)
- `sanitize("access_token=abcdef123456")` → unchanged (LEAK)
- `sanitize("client_secret=abcdef123456")` → unchanged (LEAK)
- `sanitize("refresh_token=abcdef123456")` → unchanged (LEAK)
- `sanitize("private_key=abcdef123456")` → unchanged (LEAK)
- `sanitize("Bearer abc\ndef_secondhalf")` → `'[redacted]def_secondhalf'` (partial LEAK)

Root cause: `\b…\b` boundaries cannot match when `_` abuts the keyword, and control characters are stripped after the token patterns. The committed `test_debug_redaction.py` only proves `secret` *without* an underscore, so the suite stayed green. Because DBG-01/SC2 explicitly name "proxy credentials, cookies, and auth tokens" (`secret_key`/`access_token`/`client_secret` are their canonical env-var shapes), the safety-net invariant is failed.

**Blocker to close:**
1. **Redaction denylist cannot mask underscore-compound credentials** — `diagnostics/redaction.py:47-50` (boundary) and `:74-80` (control-char ordering). Fix the boundary (`(?<![A-Za-z0-9_])`) and/or add the compound names, strip control chars before token patterns, and add the missing negative cases to `test_debug_redaction.py`.

**Non-blocking observations (recommend addressing, not goal-blocking):**
- **W-2:** the strongest control (`_settings_secrets` → `SecretRegistry`) has no committed test coverage; the verifier proved it works with a direct probe, but a regression would be silent. Add the CLI test from the review.
- **W-3 / I-1…I-4:** presence-only assertions, unquoted values, duplicate sink construction, line-level (not value-level) length cap, and the `_CONTROL_CHARS` identity check — quality hardening.

---

_Verified: 2026-10-04T08:31:05Z_
_Verifier: Claude (gsd-verifier)_
