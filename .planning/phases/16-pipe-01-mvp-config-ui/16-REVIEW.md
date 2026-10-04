---
phase: 16-pipe-01-mvp-config-ui
reviewed: 2026-10-04T19:20:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - backend/src/backend/infrastructure/yaml_pipeline_config_validator.py
  - tests/unit/test_http_pipeline_config.py
  - tests/unit/test_pipeline_config_validator.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 16: Code Review Report (incremental re-review — CR-01 fix)

**Reviewed:** 2026-10-04T19:20:00Z
**Depth:** standard
**Files Reviewed:** 3
**Scope:** changes since prior review commit `312345e084b2104b8eb22cae38e2d827eaf30287` (CR-01 remediation: `_UNREADABLE_MESSAGE` + `except yaml.YAMLError`, plus its unit/HTTP tests)
**Status:** issues_found

## Summary

This increment is the CR-01 remediation: a sibling `except yaml.YAMLError` handler
added *after* the existing `MarkedYAMLError` and `RecursionError` handlers, mapping
unmarked YAML parse errors (`yaml.reader.ReaderError`, raised for
non-printable/control characters) to a structured
`PipelineConfigValidationError(path="", message="Документ содержит недопустимые символы")`
instead of letting them escape `validate()` as an unhandled HTTP 500. One unit test and
one HTTP test were added.

I verified the delivered behavior on the current state of all three files:

- The `except` order is correct (subclass `MarkedYAMLError` first, then `RecursionError`,
  then the catch-all `yaml.YAMLError`), so marked parse errors keep their precise
  message/line and only genuinely unmarked errors take the new branch.
- Both new tests pass; the full two-file suite is green (29 passed).
- A direct probe of the validator (`\x00`, `\x1f`, `\x7f`, lone surrogate `\ud800`,
  `\ufeff`-BOM, emoji+control mix, deep flow nesting, undefined alias, complex/unhashable
  keys, python tags, empty/multi-doc/list-root/non-string-key documents) produced a
  structured reject in every case — **no unhandled exception** remained.

**Prior CR-01 is resolved.** The increment introduces no new correctness or security
defect. Two pre-existing Info-level items remain open because they were explicitly
skipped (`fix_scope=critical_warning`) and are still visible in the current files.

No source files were modified (review is read-only).

## Narrative Findings (AI reviewer)

### Prior CR-01 — RESOLVED (not a finding)

`backend/src/backend/infrastructure/yaml_pipeline_config_validator.py:117-121` now catches
`yaml.YAMLError` and maps it to a structured, document-level reject with
`line=None`. `yaml.reader.ReaderError` is a `yaml.YAMLError` but not a
`yaml.MarkedYAMLError`, so the added clause is exactly what closes the escape. The
catch-all is accurate for load-time (`ReaderError` is the only unmarked `YAMLError`
subclass reachable from `yaml.load`) and is ordered after the more specific handlers.
The accompanying tests
(`test_unreadable_control_char_document_is_rejected_not_unmarked_yaml_error`,
`test_put_control_char_yaml_returns_400_not_500`) exercise both the adapter boundary and
the route contract (400 + top-level `{"errors":[...]}` + `save_count == 0`).

## Critical Issues

None.

## Warnings

None.

## Info

### IN-01: `_TOO_DEEP_MESSAGE` is English while every other hand-authored document-level message is Russian

**File:** `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py:30-32`
**Issue:** `_OVER_CAP_MESSAGE` (`"Документ конфига превышает допустимый размер"`),
`_NOT_A_TEXT_OBJECT_MESSAGE` (`"Ожидается объект с текстовыми ключами"`) and the newly
added `_UNREADABLE_MESSAGE` (`"Документ содержит недопустимые символы"`) are Russian, but
`_TOO_DEEP_MESSAGE = "YAML nesting too deep (exceeds parser limit)"` is the lone English
document-level message. The route forwards `error.to_dict()` unchanged
(`interface/http/routes/admin.py:582-585`) and the admin UI renders the server text
verbatim (D-05), so this one reject case surfaces English copy in an otherwise
Russian-language admin surface. This is the same IN-01 raised in the prior review; it
remains in the current file. (Field-level Pydantic messages are also English, but those
are library-generated; the inconsistency here is between the module's own hand-authored
document-level messages.)
**Fix:** Use a Russian string consistent with its siblings and update the two assertions:
```python
_TOO_DEEP_MESSAGE = "Документ YAML имеет слишком глубокую вложенность"
```
Then update `tests/unit/test_pipeline_config_validator.py:217` and
`tests/unit/test_http_pipeline_config.py:314-316` (and the probe note in
`16-VERIFICATION.md:171`) to the new literal.

### IN-02: Deep-nesting tests pin a depth coupled to the interpreter recursion limit and duplicate message literals

**File:** `tests/unit/test_pipeline_config_validator.py:209`, `tests/unit/test_http_pipeline_config.py:308`
**Issue:** Both deep-nesting tests hard-code `("[" * 3000) + ("]" * 3000)` and assert the
`RecursionError` path. That only holds while `sys.getrecursionlimit()` stays near its
default (1000): if any code in the process raises the limit above the nesting depth,
PyYAML parses the document and the tests fail as "DID NOT RAISE"/wrong status instead of
exercising the intended branch. (No `setrecursionlimit` exists in the repo today, so this
is a latent reliability/maintenance concern, not a present failure.) Separately, the
production message strings are re-typed as literals at four assertion sites
(`test_pipeline_config_validator.py:217,238`; `test_http_pipeline_config.py:314-316,332-334`),
so a message change must be edited in lockstep with the tests. Both tests currently pass.
**Fix:** Derive the depth from the live limit so the `RecursionError` assertion stays
robust, and import/export the constants instead of duplicating literals:
```python
import sys

depth = sys.getrecursionlimit() + 500
document = "[" * depth + "]" * depth
```
```python
from backend.infrastructure.yaml_pipeline_config_validator import (
    MAX_PIPELINE_CONFIG_CHARS,
    PipelineConfigModel,
    YamlPipelineConfigValidator,
    _TOO_DEEP_MESSAGE,
    _UNREADABLE_MESSAGE,
)
```

---

_Reviewed: 2026-10-04T19:20:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
