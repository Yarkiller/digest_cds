"""Ports package for data-collection ingestion contracts."""

from data_collection.ports.article_generator import ArticleGenerator
from data_collection.ports.transcript_provider import TranscriptProvider

__all__ = ["ArticleGenerator", "TranscriptProvider"]
