"""Shared digest email HTML renderers (ADUX-02/03, D-07/D-11/D-13).

Pure helpers — no FastAPI/Supabase. Stdlib html.escape only.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

DEFAULT_SITE_URL = "http://127.0.0.1:5173"


def render_interstitial_html(text: str) -> str:
    """Escape + split interstitial/intro text into HTML paragraphs (D-13)."""
    # Stub for RED — empty until GREEN.
    return ""


def render_material_email_block(
    *,
    title: str,
    dek: str | None,
    slug: str,
    site_url: str = DEFAULT_SITE_URL,
) -> str:
    """Title + optional dek + Читать → absolute material link (D-11)."""
    # Stub for RED — empty until GREEN.
    return ""


def render_email_html(
    *,
    intro: str = "",
    blocks: Sequence[Mapping[str, Any]] | None = None,
    site_url: str = DEFAULT_SITE_URL,
) -> str:
    """Compose intro + ordered material/text blocks into email HTML (D-07)."""
    # Stub for RED — empty until GREEN.
    return ""
