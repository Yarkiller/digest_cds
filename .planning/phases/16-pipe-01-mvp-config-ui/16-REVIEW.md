---
phase: 16-pipe-01-mvp-config-ui
reviewed: 2026-10-04T18:45:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - backend/src/backend/infrastructure/yaml_pipeline_config_validator.py
  - tests/unit/test_http_pipeline_config.py
  - tests/unit/test_pipeline_config_validator.py
findings:
  critical: 1
  warning: 0
  info: 2
  total: 3
status: issues_found
---

# Phase 16: Code Review Report (incremental re-review — WR-02 fix)

**Reviewed:** 2026-10-04T18:45:00Z
**Depth:** standard
**Files Reviewed:** 3
**Scope:** changes since prior review commit `6b9e8581b79834de897033487fdc32f8d26e2018` (+47 lines)
**Status:** issues_found

## Summary

This increment is the WR-02 remediation: a `except RecursionError` handler around
`yaml.load` in `yaml_pipeline_config_validator.py`, mapping deep flow-nesting to a
structured `PipelineConfigValidationError` (`_TOO_DEEP_MESSAGE`), plus one unit test and
one HTTP test. I verified the delivered behavior: both new tests pass, and a deep document
(`"["*3000 + "]"*3000`) is now mapped to
`PipelineConfigError(path="", message="YAML nesting too deep (exceeds parser limit)")`
instead of an unhandled `RecursionError` (confirmed by direct probe).

However, the fix closes only **half** of the prior WR-02. The prior finding explicitly
named two escapes: `RecursionError` **and** "a bare `yaml.YAMLError` raised without marks."
Only `RecursionError` was caught. The sibling bare-`yaml.YAMLError` path (`yaml.reader.ReaderError`,
raised for non-printable/control characters) still propagates out of `validate()` and yields
an unhandled **HTTP 500** on `PUT /admin/pipeline/config` — reproduced end-to-end at the
route layer (see CR-01). This is the same defect class the fix was meant to eliminate, so
the contract "never an unhandled 500 for user-supplied text" is still not met.

No source files were modified (review is read-only).

## Structural Findings (fallow)

None provided for this increment.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Deep-nesting fix is incomplete — bare `yaml.YAMLError` (`ReaderError`) still escapes as HTTP 500

**File:** `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py:95-112`
**Issue:** The only `yaml` exception handlers are `except yaml.MarkedYAMLError` (line 95)
and the new `except RecursionError` (line 106). `yaml.reader.ReaderError` is a subclass of
`yaml.YAMLError` but **not** of `yaml.MarkedYAMLError`, and it is raised by
`Reader.check_printable` when the document contains a non-printable/control character
(e.g. `\x00`, `\x01`, `\x1f`, `\x7f`) — a payload a legitimate SPA client can emit (pasted
text with stray control bytes, or `\u0000` in JSON) and well under the 20 000-char cap.
There is no global FastAPI exception handler in `backend/src` for `YAMLError`, and the
route only catches `PipelineConfigValidationError` / `PersistenceError`
(`interface/http/routes/admin.py:579-590`), so the exception surfaces as an unhandled 500 —
contradicting the module docstring ("never a silent accept, never an execution path") and
PIPE-02's structured-400 contract.

Reproduced end-to-end (project venv, real validator via the HTTP test harness):

```text
PUT /admin/pipeline/config  body={"yaml": "template: lecture\nroles:\n  - ds\nlanguage: \x00ru\nmax_chars: 100\n"}
-> yaml.reader.ReaderError: unacceptable character #x0000 ... position 42   (unhandled; 500 in production)
```

The prior WR-02 fix text already called this out ("The same is true for a bare
`yaml.YAMLError` raised without marks") and recommended `except (yaml.YAMLError, RecursionError)`.
The shipped fix used a narrower `except RecursionError` only.

**Fix:** Add a sibling `except yaml.YAMLError` *after* the `MarkedYAMLError` handler
(subclass first) so unmarked parse/reader errors also map to a structured reject. Use a
distinct, accurate message rather than reusing `_TOO_DEEP_MESSAGE`:

```python
_UNREADABLE_MESSAGE = "Документ содержит недопустимые символы"

        try:
            data = yaml.load(yaml_text, Loader=_StrictSafeLoader)
        except yaml.MarkedYAMLError as exc:
            mark = exc.problem_mark
            raise PipelineConfigValidationError(
                (
                    PipelineConfigError(
                        path="",
                        line=(mark.line + 1) if mark is not None else None,
                        message=str(exc.problem or exc),
                    ),
                )
            ) from exc
        except RecursionError as exc:
            # WR-02: deep flow collections overflow the recursive scanner.
            raise PipelineConfigValidationError(
                (PipelineConfigError(path="", message=_TOO_DEEP_MESSAGE),)
            ) from exc
        except yaml.YAMLError as exc:
            # ReaderError and other unmarked YAMLErrors (e.g. non-printable chars).
            raise PipelineConfigValidationError(
                (PipelineConfigError(path="", message=_UNREADABLE_MESSAGE),)
            ) from exc
```

Add a RED test first (mandatory TDD) covering a control-character document at both the
validator unit level and the HTTP level (assert 400 + top-level `{"errors":[...]}` +
`save_count == 0`).

## Warnings

None.

## Info

### IN-01: `_TOO_DEEP_MESSAGE` is English while sibling document-level messages are Russian

**File:** `backend/src/backend/infrastructure/yaml_pipeline_config_validator.py:30-32`
**Issue:** `_OVER_CAP_MESSAGE` and `_NOT_A_TEXT_OBJECT_MESSAGE` are Russian, but the new
`_TOO_DEEP_MESSAGE = "YAML nesting too deep (exceeds parser limit)"` is English. D-05
requires error rows to be rendered as verbatim server text (the route forwards
`error.to_dict()` unchanged), so a Russian-language admin UI will surface an English
message for this one reject case. Inconsistent with the other two document-level messages.
**Fix:** Use a Russian message consistent with the siblings (e.g.
`"Документ YAML имеет слишком глубокую вложенность"`) and update
`test_pipeline_config_validator.py:217` and `test_http_pipeline_config.py:314` accordingly.

### IN-02: New tests hard-code a nesting depth coupled to the interpreter recursion limit

**File:** `tests/unit/test_pipeline_config_validator.py:209`, `tests/unit/test_http_pipeline_config.py:308`
**Issue:** Both tests pin `"[ " "*3000` and assert the `RecursionError` path. This only
holds while `sys.getrecursionlimit()` stays near its default (1000): if any code in the
suite/process raises the limit above the nesting depth, PyYAML parses the document and the
tests fail ("DID NOT RAISE"/wrong status) rather than exercising the intended branch. The
tests also duplicate the literal English message string instead of sharing a constant, so
the message and its assertions must be edited in lockstep (see IN-01). Both tests currently
pass; this is a maintenance/flakiness note, not a present failure.
**Fix:** Derive the depth from the live limit (e.g.
`depth = sys.getrecursionlimit() + 500`) so the RecursionError assertion stays robust, and/or
export the message constant for tests to import instead of duplicating the literal.

---

_Reviewed: 2026-10-04T18:45:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
