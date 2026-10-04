"""Pipeline config domain model — PIPE-01/PIPE-03 (D-08, D-11, D-12, D-13).

The PIPE-01 MVP config is a raw YAML document persisted as a single global row
behind the PipelineConfigRepository port (D-08). The YAML text is the source of
truth (D-13); the backend owns schema validation and the SPA renders the
``{yaml, updated_at}`` DTO verbatim (D-11). This module carries no yaml/pydantic
imports — parsing stays in the infrastructure validator adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PipelineConfig:
    """A saved pipeline config document plus its last-saved timestamp (D-08/D-11)."""

    yaml: str
    updated_at: datetime | None
