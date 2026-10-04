"""StderrDiagnostics — format and emit secret-safe stage lines (D-01…D-03, D-13).

Concrete implementation of ``StageDiagnostics``: owns the injected ``Clock``
(elapsed ms + ``[HH:MM:SS]`` timestamp), the allowlist filter, and redaction.
Emits exclusively via ``typer.echo(..., err=True)`` (or an injected stream) so
the machine-readable stdout contract is never contaminated.
"""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import TextIO

import typer

from ingestion_service.application.ports.diagnostics import Clock, DebugValue
from ingestion_service.diagnostics.redaction import (
    ALLOWED_KEYS,
    SecretRegistry,
    sanitize,
)


class SystemClock:
    """Production ``Clock`` backed by ``time.monotonic`` / ``datetime.now``."""

    def monotonic(self) -> float:
        return time.monotonic()

    def now(self) -> datetime:
        return datetime.now()


class StderrDiagnostics:
    """Formats one summarized debug line per stage and writes it to stderr."""

    def __init__(
        self,
        clock: Clock,
        secrets: Sequence[str] = (),
        stream: TextIO | None = None,
    ) -> None:
        self._clock = clock
        self._registry = SecretRegistry(secrets)
        self._stream = stream
        self._started_at: float | None = None

    def stage_started(self, stage: str) -> None:
        self._started_at = self._clock.monotonic()

    def stage_completed(self, stage: str, signals: Mapping[str, DebugValue]) -> None:
        self._emit(stage, signals, elapsed_ms=self._elapsed_ms())

    def stage_failed(self, stage: str, *, reason: str, exit_code: int) -> None:
        self._emit(
            stage,
            {"reason": reason, "exit_code": exit_code},
            elapsed_ms=self._elapsed_ms(),
        )

    def config_error(self, *, error_type: str, message: str) -> None:
        # D-12: no IngestError is minted for pre-video config failures.
        self._emit(
            "config",
            {"error_type": error_type, "message": message},
            elapsed_ms=0,
        )

    def _elapsed_ms(self) -> int:
        if self._started_at is None:
            return 0
        elapsed = int((self._clock.monotonic() - self._started_at) * 1000)
        self._started_at = None
        return elapsed

    def _emit(
        self,
        stage: str,
        signals: Mapping[str, DebugValue],
        *,
        elapsed_ms: int,
    ) -> None:
        parts = [f"stage={stage}", f"elapsed_ms={elapsed_ms}"]
        for key, value in signals.items():
            if key not in ALLOWED_KEYS:
                continue
            parts.append(f"{key}={value}")
        timestamp = self._clock.now().strftime("%H:%M:%S")
        line = sanitize(f"[{timestamp}] debug " + " ".join(parts), registry=self._registry)
        if self._stream is None:
            typer.echo(line, err=True)
        else:
            self._stream.write(line + "\n")
