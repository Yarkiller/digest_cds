"""score_factors honesty helper — ADMIN-05 / D-79 (≥2 labels or empty for «обоснование недоступно»)."""

from __future__ import annotations

from backend.domain.shortlist import honest_factor_labels


def test_honest_factor_labels_returns_labels_when_factors_list_has_two_or_more() -> None:
    labels = honest_factor_labels(
        {
            "factors": [
                {"label": "Релевантность"},
                {"label": "Свежесть"},
            ]
        }
    )
    assert labels == ["Релевантность", "Свежесть"]


def test_honest_factor_labels_returns_labels_from_flat_map_keys() -> None:
    labels = honest_factor_labels({"Релевантность": 0.8, "Свежесть": 0.6})
    assert labels == ["Релевантность", "Свежесть"]


def test_honest_factor_labels_empty_when_fewer_than_two_readable() -> None:
    assert honest_factor_labels({}) == []
    assert honest_factor_labels({"factors": [{"label": "Только один"}]}) == []
    assert honest_factor_labels({"Единственный": 1.0}) == []
    assert honest_factor_labels({"factors": [{"label": ""}, {"label": "  "}]}) == []


def test_honest_factor_labels_falls_back_to_flat_keys_when_factors_list_empty() -> None:
    """WR-02: empty ``factors: []`` must not shadow ≥2 readable flat keys (demo seed honesty)."""
    labels = honest_factor_labels(
        {
            "релевантность теме недели": 0.9,
            "качество источников": 0.85,
            "factors": [],
        }
    )
    assert labels == ["релевантность теме недели", "качество источников"]


def test_honest_factor_labels_ignores_blank_labels_in_list() -> None:
    labels = honest_factor_labels(
        {
            "factors": [
                {"label": "  "},
                {"label": "A"},
                {"label": "B"},
            ]
        }
    )
    assert labels == ["A", "B"]
