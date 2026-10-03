"""email_render + email_chrome — interstitial HTML matrix and ban asserts (ADUX-02/03/04).

Closed ban tokens (D-18): test-header, test_header, testheader — assert-only (D-17/D-19).
"""

from __future__ import annotations

from backend.application.use_cases.email_render import (
    render_email_html,
    render_interstitial_html,
    render_material_email_block,
)
from backend.domain.email_chrome import FORBIDDEN_LOWER, contains_forbidden_chrome


def test_render_interstitial_html_empty_returns_empty() -> None:
    assert render_interstitial_html("") == ""


def test_render_interstitial_html_whitespace_only_returns_empty() -> None:
    assert render_interstitial_html("   \n\t  ") == ""


def test_render_interstitial_html_single_paragraph() -> None:
    assert render_interstitial_html("hello") == "<p>hello</p>"


def test_render_interstitial_html_two_paragraphs_via_blank_line() -> None:
    assert render_interstitial_html("one\n\ntwo") == "<p>one</p><p>two</p>"


def test_render_interstitial_html_single_newline_becomes_br() -> None:
    assert render_interstitial_html("a\nb") == "<p>a<br>b</p>"


def test_render_interstitial_html_strips_leading_trailing_whitespace() -> None:
    assert render_interstitial_html("  padded  ") == "<p>padded</p>"


def test_render_interstitial_html_escapes_angle_brackets_and_quotes() -> None:
    out = render_interstitial_html('<tag attr="x">')
    assert "<tag" not in out
    assert "&lt;tag" in out
    assert "&quot;x&quot;" in out
    assert out.startswith("<p>") and out.endswith("</p>")


def test_render_material_email_block_title_dek_and_read_link() -> None:
    html = render_material_email_block(
        title="My Title",
        dek="Short dek",
        slug="my-slug",
        site_url="http://127.0.0.1:5173",
    )
    assert "My Title" in html
    assert "Short dek" in html
    assert 'href="http://127.0.0.1:5173/materials/my-slug"' in html
    assert "Читать →" in html
    assert "/issues/" not in html


def test_render_material_email_block_omits_empty_dek() -> None:
    html = render_material_email_block(
        title="Only title",
        dek="  ",
        slug="only",
        site_url="http://example.test",
    )
    assert "Only title" in html
    assert html.count("<p>") == 1  # link paragraph only
    assert "Читать →" in html


def test_render_material_email_block_defaults_site_url() -> None:
    html = render_material_email_block(title="T", dek=None, slug="s")
    assert 'href="http://127.0.0.1:5173/materials/s"' in html


def test_render_material_email_block_escapes_title_and_dek() -> None:
    html = render_material_email_block(
        title="<bad>",
        dek='x"y',
        slug="safe",
        site_url="http://127.0.0.1:5173",
    )
    assert "<bad>" not in html
    assert "&lt;bad&gt;" in html
    assert "&quot;y" in html or "&#x27;" in html or "&quot;" in html


def test_render_email_html_applies_interstitial_to_intro_and_includes_material() -> None:
    html = render_email_html(
        intro="Intro para one\n\nIntro para two",
        blocks=(
            {"kind": "material", "title": "Seeded", "dek": "Dek", "slug": "seeded"},
            {"kind": "text", "text": "Bridge\n\nMore"},
        ),
        site_url="http://127.0.0.1:5173",
    )
    assert "<p>Intro para one</p><p>Intro para two</p>" in html
    assert "Seeded" in html
    assert 'href="http://127.0.0.1:5173/materials/seeded"' in html
    assert "Читать →" in html
    assert "<p>Bridge</p><p>More</p>" in html
    assert "/issues/" not in html


def test_render_email_html_defaults_site_url() -> None:
    html = render_email_html(
        intro="",
        blocks=({"kind": "material", "title": "T", "dek": None, "slug": "x"},),
    )
    assert 'href="http://127.0.0.1:5173/materials/x"' in html


def test_forbidden_lower_closed_list() -> None:
    assert FORBIDDEN_LOWER == ["test-header", "test_header", "testheader"]


def test_contains_forbidden_chrome_detects_hyphen_underscore_concat_case_insensitive() -> None:
    assert contains_forbidden_chrome("prefix TEST-HEADER suffix")
    assert contains_forbidden_chrome("xx Test_Header yy")
    assert contains_forbidden_chrome("testHeader")
    assert not contains_forbidden_chrome("clean editorial copy")


def test_clean_render_email_html_fixture_has_no_forbidden_chrome() -> None:
    html = render_email_html(
        intro="Weekly note",
        blocks=(
            {
                "kind": "material",
                "title": "Clean Title",
                "dek": "Clean dek",
                "slug": "clean-title",
            },
        ),
        site_url="http://127.0.0.1:5173",
    )
    assert not contains_forbidden_chrome(html)


def test_email_render_module_does_not_import_or_call_ban_helper() -> None:
    """D-17: renderers must not filter via contains_forbidden_chrome (assert-only)."""
    from pathlib import Path

    src = Path(render_email_html.__code__.co_filename).read_text(encoding="utf-8")
    assert "email_chrome" not in src
    assert "contains_forbidden_chrome" not in src
    assert "FORBIDDEN_LOWER" not in src


def test_python_forbidden_lower_matches_js_mirror() -> None:
    """D-18: Python FORBIDDEN_LOWER must equal web/src/utils/forbiddenChrome.js list order/values."""
    import ast
    import re
    from pathlib import Path

    js_path = (
        Path(__file__).resolve().parents[2] / "web" / "src" / "utils" / "forbiddenChrome.js"
    )
    assert js_path.is_file(), f"missing JS ban mirror: {js_path}"
    js_src = js_path.read_text(encoding="utf-8")
    match = re.search(
        r"export\s+const\s+FORBIDDEN_LOWER\s*=\s*(\[[^\]]*\])",
        js_src,
        flags=re.DOTALL,
    )
    assert match is not None, "FORBIDDEN_LOWER export not found in forbiddenChrome.js"
    js_list = ast.literal_eval(match.group(1))
    assert js_list == FORBIDDEN_LOWER
    assert "containsForbiddenChrome" in js_src
