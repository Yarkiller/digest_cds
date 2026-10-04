"""Strict YAML + schema validator adapter — PIPE-02 (D-01..D-07, T-16-05/06/09).

This is the ONLY module that parses YAML. It implements the
``PipelineConfigValidator`` port with a strict ``SafeLoader`` subclass (syntax +
duplicate keys + non-string top-level keys + empty/multi-document) plus a fixed
Pydantic ``extra="forbid"`` schema (keys/types/required). Parse and schema
failures are mapped at this adapter boundary into a
``PipelineConfigValidationError`` carrying ``PipelineConfigError(path, line?, message)``
entries — never a silent accept, never an execution path.

``yaml`` and ``pydantic`` must not be imported from ``domain/`` or
``application/use_cases/`` (architecture.mdc); this file lives in infrastructure.
"""

from __future__ import annotations

from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

from backend.domain.errors import PipelineConfigValidationError
from backend.domain.pipeline_config import PipelineConfigError

# Server-side cap rejected before parse (T-16-07: YAML alias / oversized document DoS).
MAX_PIPELINE_CONFIG_CHARS = 20000

_OVER_CAP_MESSAGE = "Документ конфига превышает допустимый размер"
_NOT_A_TEXT_OBJECT_MESSAGE = "Ожидается объект с текстовыми ключами"
_TOO_DEEP_MESSAGE = "YAML nesting too deep (exceeds parser limit)"


class _StrictSafeLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys instead of silently last-wins."""

    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Any, Any]:
        if isinstance(node, MappingNode):
            seen: set[Any] = set()
            for key_node, _value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                try:
                    hash(key)
                except TypeError:
                    continue
                if key in seen:
                    raise ConstructorError(
                        "while constructing a mapping",
                        node.start_mark,
                        f"found duplicate key ({key!r})",
                        key_node.start_mark,
                    )
                seen.add(key)
        return super().construct_mapping(node, deep=deep)


class PipelineConfigModel(BaseModel):
    """Fixed, documented pipeline-config schema — unknown keys forbidden (D-01/D-02/D-06).

    The four-key set deliberately excludes any secret/credential key (PIPE-03) and
    any ``score_factors`` weight (D-01; ADUX-06 stays on the honest-empty path).
    """

    model_config = ConfigDict(extra="forbid")

    template: Literal["lecture", "podcast"]
    roles: list[Literal["employee", "analyst", "ds"]] = Field(min_length=1)
    language: str = Field(min_length=1)
    max_chars: int = Field(gt=0)


def _loc_to_dot_sep(loc: tuple[Any, ...]) -> str:
    """Render a Pydantic ``loc`` tuple as a dotted/indexed path (e.g. ``roles[0]``)."""
    path = ""
    for index, part in enumerate(loc):
        if isinstance(part, str):
            path += ("." if index > 0 else "") + part
        else:
            path += f"[{part}]"
    return path


class YamlPipelineConfigValidator:
    """Server-authoritative validator implementing the ``PipelineConfigValidator`` port."""

    def validate(self, yaml_text: str) -> None:
        if len(yaml_text) > MAX_PIPELINE_CONFIG_CHARS:
            raise PipelineConfigValidationError(
                (PipelineConfigError(path="", message=_OVER_CAP_MESSAGE),)
            )

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
            # WR-02: deeply nested flow collections (< cap) overflow the parser's
            # recursive scanner. Map it to a structured reject at this boundary so
            # the route returns a 400 {"errors":[...]} instead of an unhandled 500.
            raise PipelineConfigValidationError(
                (PipelineConfigError(path="", message=_TOO_DEEP_MESSAGE),)
            ) from exc

        if not isinstance(data, dict) or not all(isinstance(key, str) for key in data):
            raise PipelineConfigValidationError(
                (PipelineConfigError(path="", message=_NOT_A_TEXT_OBJECT_MESSAGE),)
            )

        try:
            PipelineConfigModel.model_validate(data)
        except ValidationError as exc:
            raise PipelineConfigValidationError(
                tuple(
                    PipelineConfigError(
                        path=_loc_to_dot_sep(error["loc"]),
                        message=error["msg"],
                    )
                    for error in exc.errors()
                )
            ) from exc
