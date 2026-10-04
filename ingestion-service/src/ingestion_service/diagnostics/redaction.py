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

DENY_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Bearer tokens must be masked before the assignment pattern below, otherwise
    # the assignment match would stop at the scheme word and leak the token value.
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^/@\s]+@"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|authorization|cookie)"
        r"\b\s*[=:]\s*\S+"
    ),
    _CONTROL_CHARS,
)


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
    """Mask secrets/denylisted values, strip control chars, cap length (never raises)."""
    if not isinstance(text, str):
        text = str(text)
    if registry is not None:
        text = registry.mask(text)
    for pattern in DENY_PATTERNS:
        if pattern is _CONTROL_CHARS:
            # Control characters are stripped, not masked, so a newline/ANSI escape
            # cannot forge extra debug lines or corrupt the terminal.
            text = pattern.sub("", text)
        else:
            text = pattern.sub(REDACTED, text)
    return text[:MAX_VALUE_LENGTH]
