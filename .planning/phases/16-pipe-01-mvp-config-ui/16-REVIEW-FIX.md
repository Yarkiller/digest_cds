---
phase: 16-pipe-01-mvp-config-ui
fixed_at: 2026-10-04T19:13:03Z
review_path: C:/Users/Yarkiller/PycharmPET-Projects/Digital_CDS/.planning/phases/16-pipe-01-mvp-config-ui/16-REVIEW.md
iteration: 1
findings_in_scope: 1
fixed: 1
skipped: 0
status: all_fixed
---

# Phase 16: Code Review Fix Report

**Fixed at:** 2026-10-04T19:13:03Z
**Source review:** `C:/Users/Yarkiller/PycharmPET-Projects/Digital_CDS/.planning/phases/16-pipe-01-mvp-config-ui/16-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 1
- Fixed: 1
- Skipped: 0

## Fixed Issues

### CR-01: Deep-nesting fix is incomplete — bare `yaml.YAMLError` (`ReaderError`) still escapes as HTTP 500

**Files modified:** `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py`, `tests/unit/test_pipeline_config_validator.py`, `tests/unit/test_http_pipeline_config.py`
**Commit:** `a63b258`
**Applied fix:**

Followed TDD (RED → GREEN):

1. **RED tests first** — added two failing tests and confirmed both failed for the expected reason (`yaml.reader.ReaderError` escaping `validate()`):
   - `tests/unit/test_pipeline_config_validator.py::test_unreadable_control_char_document_is_rejected_not_unmarked_yaml_error`
   - `tests/unit/test_http_pipeline_config.py::test_put_control_char_yaml_returns_400_not_500` (asserts `400` + top-level `{"errors":[...]}` + `save_count == 0`)
2. **Minimal production fix** — added the `_UNREADABLE_MESSAGE = "Документ содержит недопустимые символы"` constant and a sibling `except yaml.YAMLError` handler *after* the `MarkedYAMLError` and `RecursionError` handlers (subclass first), mapping unmarked parse/reader errors to a structured `PipelineConfigValidationError`. This closes the second half of the prior WR-02 so user-supplied text no longer surfaces as an unhandled HTTP 500.
3. **Verification** — re-read the modified section; `ast.parse` syntax check passed; ran the two new tests plus the full `test_pipeline_config_validator.py` and `test_http_pipeline_config.py` suites: **29 passed**.

## Skipped Issues

Findings **IN-01** and **IN-02** are Info-level and out of scope for `fix_scope=critical_warning`; they were not fixed.

### IN-01: `_TOO_DEEP_MESSAGE` is English while sibling document-level messages are Russian

**File:** `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py:30-32`
**Reason:** out of scope (`critical_warning`)
**Original issue:** `_TOO_DEEP_MESSAGE` is English while `_OVER_CAP_MESSAGE` and `_NOT_A_TEXT_OBJECT_MESSAGE` are Russian, so a Russian-language admin UI surfaces an English message for the deep-nesting reject case.

### IN-02: New tests hard-code a nesting depth coupled to the interpreter recursion limit

**File:** `tests/unit/test_pipeline_config_validator.py:209`, `tests/unit/test_http_pipeline_config.py:308`
**Reason:** out of scope (`critical_warning`)
**Original issue:** Both deep-nesting tests pin `"[ " "*3000` and duplicate the literal English message string; they would break if `sys.getrecursionlimit()` were raised. Maintenance/robustness note, not a present failure.

---

_Fixed: 2026-10-04T19:13:03Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
