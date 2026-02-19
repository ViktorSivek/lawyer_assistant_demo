import os

import pytest

from mcp_server.checks import check_whitespace
from mcp_server.docx_parser import (
    get_all_sections_summary,
    get_section_content,
    load_document_structure,
)
from tests.ground_truth import GROUND_TRUTH


TEST_DOC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "documents",
    "test_smlouva.docx",
)


def _load_whitespace_issues():
    result = check_whitespace(TEST_DOC_PATH)
    assert "issues" in result, result
    return result["issues"]


def _filter_issue_types(issues, issue_type: str):
    return [issue for issue in issues if issue["type"] == issue_type]


def test_whitespace_double_spaces():
    issues = _load_whitespace_issues()
    matches = _filter_issue_types(issues, "double_space")
    assert len(matches) >= len(GROUND_TRUTH["whitespace"]["double_space"])


def test_whitespace_trailing_spaces():
    issues = _load_whitespace_issues()
    matches = _filter_issue_types(issues, "trailing_whitespace")
    assert len(matches) >= len(GROUND_TRUTH["whitespace"]["trailing_whitespace"])


def test_whitespace_leading_spaces():
    issues = _load_whitespace_issues()
    matches = _filter_issue_types(issues, "leading_whitespace")
    assert len(matches) >= len(GROUND_TRUTH["whitespace"]["leading_whitespace"])


def test_whitespace_consecutive_blanks():
    issues = _load_whitespace_issues()
    matches = _filter_issue_types(issues, "consecutive_blank_paragraphs")
    assert len(matches) >= len(
        GROUND_TRUTH["whitespace"]["consecutive_blank_paragraphs"]
    )


def test_load_structure_headings():
    structure = load_document_structure(TEST_DOC_PATH)
    assert structure["heading_count"] >= 20
    assert structure["heading_tree"], "Heading tree should not be empty"


def test_section_content_article_2():
    section = get_section_content(TEST_DOC_PATH, "Článek 2 – Předmět smlouvy")
    assert "Předmětem této smlouvy" in section["content"]


def test_sections_summary_verbatim_paragraph_overlap():
    """The verbatim duplicate is a single paragraph inside two different
    sections (Article 7 and Article 9).  Whole-section hashes differ,
    so we verify via the preview text that the shared paragraph appears
    in both sections' previews."""
    art7 = get_section_content(TEST_DOC_PATH, "Článek 7 – Smluvní pokuty")
    art9 = get_section_content(TEST_DOC_PATH, "Článek 9 – Odstoupení od smlouvy")
    shared = (
        "V případě prodlení Zhotovitele s termínem dokončení díla dle čl. 4 "
        "je Objednatel oprávněn požadovat smluvní pokutu ve výši 0,05 %"
    )
    assert shared in art7["content"], "Shared paragraph missing from Article 7"
    assert shared in art9["content"], "Shared paragraph missing from Article 9"


def test_enumeration_bad_article_3():
    from mcp_server.checks import check_enumerations  # noqa: WPS433

    result = check_enumerations(TEST_DOC_PATH)
    assert any(
        issue.get("section") == "3.1 Platební podmínky"
        for issue in result.get("issues", [])
    )


def test_enumeration_bad_article_8():
    from mcp_server.checks import check_enumerations  # noqa: WPS433

    result = check_enumerations(TEST_DOC_PATH)
    assert any(
        issue.get("section") == "Článek 8 – Záruční podmínky"
        for issue in result.get("issues", [])
    )


def test_enumeration_good_article_2():
    from mcp_server.checks import check_enumerations  # noqa: WPS433

    result = check_enumerations(TEST_DOC_PATH)
    assert not any(
        issue.get("section") == "2.1 Rozsah díla"
        for issue in result.get("issues", [])
    )


def test_reference_invalid_priloha_5():
    from mcp_server.checks import extract_and_validate_references  # noqa: WPS433

    result = extract_and_validate_references(TEST_DOC_PATH)
    assert any(
        ref.get("text") == "příloha č. 5" for ref in result.get("invalid", [])
    )


def test_reference_valid_article_12():
    # Article 12 exists as a heading ("Článek 12 – Doplňující ujednání"),
    # so the reference in Article 7 is structurally valid even though the
    # section contains only boilerplate — semantic validation is out of scope.
    from mcp_server.checks import extract_and_validate_references  # noqa: WPS433

    result = extract_and_validate_references(TEST_DOC_PATH)
    assert not any(
        ref.get("text") == "článek 12" for ref in result.get("invalid", [])
    )


def test_reference_field_code_violations():
    from mcp_server.checks import extract_and_validate_references  # noqa: WPS433

    result = extract_and_validate_references(TEST_DOC_PATH)
    assert result.get("field_code_violations")