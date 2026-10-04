"""Secret-safe redaction for opt-in diagnostics (D-07, D-08, D-09).

Pure, I/O-free module: an allowlist of emittable signal keys, an exact-value
``SecretRegistry`` built from runtime ``Settings`` secrets, and a never-raising
``sanitize`` safety net that masks known secrets and strips control characters.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

ALLOWED_KEYS: frozenset[str] = frozenset(
    {
        "stage",
        "elapsed_ms",
        "video_id",
        "transcript_chars",
        "transcript_words",
        "language",
        "template",
        "response_chars",
        "material_id",
        "slug",
        "batch_id",
        "rank",
        "already_saved",
        "reason",
        "exit_code",
        "error_type",
        "message",
    }
)

REDACTED = "[redacted]"
MAX_VALUE_LENGTH = 256

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


class SecretRegistry:
    """Exact runtime secret values; masks each occurrence with ``[redacted]``."""

    def __init__(self, secrets: Sequence[str] = ()) -> None:
        unique = {secret for secret in secrets if secret and len(secret) >= 4}
        self._secrets = sorted(unique, key=len, reverse=True)

    def mask(self, text: str) -> str:
        for secret in self._secrets:
            text = text.replace(secret, REDACTED)
        return text


def sanitize(text: str, *, registry: SecretRegistry | None = None) -> str:
    """Mask registered secrets, strip control chars, and cap length (never raises)."""
    if not isinstance(text, str):
        text = str(text)
    if registry is not None:
        text = registry.mask(text)
    text = _CONTROL_CHARS.sub("", text)
    return text[:MAX_VALUE_LENGTH]
