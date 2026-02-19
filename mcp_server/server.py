"""FastMCP server for analyzing Czech legal .docx documents."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastmcp import FastMCP

from mcp_server.checks import check_enumerations, check_whitespace
from mcp_server.docx_parser import (
    get_all_sections_summary,
    get_section_content,
    load_document_structure,
)

mcp = FastMCP("Legal Document Analyzer")


# ── parser tools ───────────────────────────────────────────────────


@mcp.tool
def tool_load_document_structure(filepath: str) -> dict:
    """Parse a .docx and return heading tree, paragraph count, and metadata.

    Args:
        filepath: Path to the .docx file.

    Returns a dict with: filepath, paragraph_count, heading_count,
    headings (flat list), and heading_tree (nested).
    """
    return load_document_structure(filepath)


@mcp.tool
def tool_get_section_content(filepath: str, heading_text: str) -> dict:
    """Return full text content under a specific heading.

    Collects all paragraphs from the heading until the next heading
    of the same or higher level.

    Args:
        filepath: Path to the .docx file.
        heading_text: Exact text of the heading to retrieve.

    Returns a dict with: heading, level, content, paragraph_count,
    subsections.
    """
    return get_section_content(filepath, heading_text)


@mcp.tool
def tool_get_all_sections_summary(filepath: str) -> dict:
    """Return compact summary for each section: preview + content hash.

    Used for quick redundancy screening — identical content_hash means
    exact duplicate text, similar previews suggest near-duplicates.

    Args:
        filepath: Path to the .docx file.

    Returns a dict with: filepath, sections (list of heading, level,
    preview, content_hash, paragraph_count).
    """
    return get_all_sections_summary(filepath)


# ── check tools ────────────────────────────────────────────────────


@mcp.tool
def tool_check_whitespace(filepath: str) -> dict:
    """Find whitespace issues in a .docx document.

    Checks for double spaces, trailing/leading whitespace, and
    consecutive blank paragraphs.

    Args:
        filepath: Path to the .docx file.

    Returns a dict with: filepath, issue_count, issues (list of
    type, paragraph_index, section, text, detail).
    """
    return check_whitespace(filepath)


@mcp.tool
def tool_check_enumerations(filepath: str) -> dict:
    """Check enumeration delimiter consistency in a .docx document.

    Detects text-pattern list items: (a)/(b), a)/b), (i)/(ii), etc.
    Reports runs where non-last items use mixed terminators (e.g. ',' and ';').

    Args:
        filepath: Path to the .docx file.

    Returns a dict with: filepath, issue_count, issues (list of
    type, paragraph_index, section, text, detail, terminators).
    """
    return check_enumerations(filepath)


# ── entrypoint ─────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
