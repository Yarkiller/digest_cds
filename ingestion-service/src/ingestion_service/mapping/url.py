"""Map InvalidYouTubeUrl → IngestError(stage=url) (D-05, D-11)."""

from __future__ import annotations

from ingestion_service.domain.errors import IngestError
from ingestion_service.url import InvalidYouTubeUrl


def map_url_error(error: InvalidYouTubeUrl) -> IngestError:
    return IngestError(
        stage="url",
        reason=error.reason,
        message=str(error),
        context=dict(error.context),
    )
