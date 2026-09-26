"""Public API for data-collection ingestion contracts (D-01, D-04)."""

from data_collection.dto.material_draft import MaterialDraft
from data_collection.dto.template_kind import TemplateKind
from data_collection.dto.transcript import Transcript
from data_collection.dto.video_metadata import VideoMetadata
from data_collection.ports.article_generator import ArticleGenerator
from data_collection.ports.transcript_provider import TranscriptProvider

__all__ = [
    "Transcript",
    "VideoMetadata",
    "MaterialDraft",
    "TemplateKind",
    "TranscriptProvider",
    "ArticleGenerator",
]
