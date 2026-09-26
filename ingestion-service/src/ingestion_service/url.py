"""YouTube URL / bare-id → video_id (CAP-01, D-01…D-05)."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
_ALLOWED_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }
)


class InvalidYouTubeUrl(Exception):
    """Raised when the input is not an allowlisted YouTube URL or bare id."""

    def __init__(self, reason: str, value: str, **context: object) -> None:
        super().__init__(f"{reason}: {value!r}")
        self.reason = reason
        self.value = value
        self.context = {"value": value, **context}


def extract_video_id(value: str) -> str:
    raw = value.strip()
    if not raw:
        raise InvalidYouTubeUrl("invalid_video_id", value)

    if _ID_RE.fullmatch(raw):
        return raw

    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if host not in _ALLOWED_HOSTS:
        raise InvalidYouTubeUrl("not_a_youtube_url", value)

    path = parsed.path or ""
    query = parse_qs(parsed.query)

    if host in {"youtu.be", "www.youtu.be"}:
        candidate = path.strip("/").split("/")[0] if path.strip("/") else ""
        return _require_id(candidate, value)

    # youtube.com / www / m — path families
    segments = [s for s in path.split("/") if s]
    if not segments:
        raise InvalidYouTubeUrl("missing_video_id", value)

    head = segments[0].lower()

    if head == "watch":
        vids = query.get("v") or []
        if not vids or not vids[0]:
            raise InvalidYouTubeUrl("missing_video_id", value)
        return _require_id(vids[0], value)

    if head in {"shorts", "embed"}:
        if len(segments) < 2:
            raise InvalidYouTubeUrl("missing_video_id", value)
        return _require_id(segments[1], value)

    raise InvalidYouTubeUrl("not_a_youtube_url", value)


def _require_id(candidate: str, value: str) -> str:
    if not _ID_RE.fullmatch(candidate):
        raise InvalidYouTubeUrl("invalid_video_id", value, candidate=candidate)
    return candidate
