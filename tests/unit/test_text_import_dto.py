"""RED→GREEN: text import DTO dedup checksum."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError


def test_text_import_dto_requires_content_sha256() -> None:
    from data_collection.dto.text_import import TextImportDto

    dto = TextImportDto(
        source_url="https://example.com/doc",
        title_hint="Doc",
        raw_text="Hello world",
        content_sha256="b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
        imported_by="admin@sberbank.ru",
        imported_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        adapter_version="1.0.0",
    )
    assert dto.source_system == "text_import"
    assert len(dto.content_sha256) == 64


def test_text_import_dto_rejects_empty_raw_text() -> None:
    from data_collection.dto.text_import import TextImportDto

    with pytest.raises(ValidationError):
        TextImportDto(
            source_url=None,
            title_hint=None,
            raw_text="",
            content_sha256="a" * 64,
            imported_by="admin@sberbank.ru",
            imported_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
            adapter_version="1.0.0",
        )
