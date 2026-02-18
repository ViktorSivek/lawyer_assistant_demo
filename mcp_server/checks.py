"""Deterministic checks — whitespace, enumerations, references."""

from __future__ import annotations

import os
import re
from typing import Any

from docx import Document

from mcp_server.docx_parser import _detect_heading_level


# ── whitespace ─────────────────────────────────────────────────────

_RE_DOUBLE_SPACE = re.compile(r"  +")


def _find_parent_heading(paragraphs, idx: int) -> str | None:
    """Walk backwards from idx to find the nearest heading."""
    for i in range(idx - 1, -1, -1):
        level = _detect_heading_level(paragraphs[i])
        if level is not None:
            return paragraphs[i].text.strip()
    return None


def check_whitespace(filepath: str) -> dict[str, Any]:
    """Find whitespace issues in a .docx document.

    Checks for:
      - Double (or more) consecutive spaces within text
      - Trailing whitespace at end of paragraph text
      - Leading whitespace at start of paragraph text
      - Consecutive blank paragraphs

    Returns:
      {filepath, issue_count, issues: [{type, paragraph_index,
       section, text, detail}, ...]}
    """
    if not os.path.isfile(filepath):
        return {"error": f"File not found: {filepath}"}

    doc = Document(filepath)
    paragraphs = doc.paragraphs
    issues: list[dict[str, Any]] = []

    prev_blank = False

    for idx, p in enumerate(paragraphs):
        text = p.text
        level = _detect_heading_level(p)

        # Skip headings themselves
        if level is not None:
            prev_blank = False
            continue

        section = _find_parent_heading(paragraphs, idx)
        is_blank = text.strip() == ""

        # Consecutive blank paragraphs
        if is_blank and prev_blank:
            issues.append({
                "type": "consecutive_blank_paragraphs",
                "paragraph_index": idx,
                "section": section,
                "text": "",
                "detail": "Multiple consecutive blank paragraphs",
            })
        prev_blank = is_blank

        if is_blank:
            continue

        # Double spaces
        for m in _RE_DOUBLE_SPACE.finditer(text):
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 20)
            context = text[start:end]
            issues.append({
                "type": "double_space",
                "paragraph_index": idx,
                "section": section,
                "text": text[:80] + ("…" if len(text) > 80 else ""),
                "detail": f"Multiple spaces at position {m.start()}: \"…{context}…\"",
            })

        # Trailing whitespace
        if text != text.rstrip():
            trailing = text[len(text.rstrip()):]
            issues.append({
                "type": "trailing_whitespace",
                "paragraph_index": idx,
                "section": section,
                "text": text.rstrip()[:80] + ("…" if len(text.rstrip()) > 80 else ""),
                "detail": f"{len(trailing)} trailing whitespace character(s)",
            })

        # Leading whitespace (skip list items — they may be indented)
        if text != text.lstrip() and not _is_list_item(p):
            leading = text[:len(text) - len(text.lstrip())]
            issues.append({
                "type": "leading_whitespace",
                "paragraph_index": idx,
                "section": section,
                "text": text.strip()[:80] + ("…" if len(text.strip()) > 80 else ""),
                "detail": f"{len(leading)} leading whitespace character(s)",
            })

    return {
        "filepath": filepath,
        "issue_count": len(issues),
        "issues": issues,
    }


def _is_list_item(paragraph) -> bool:
    """Check if a paragraph is a Word list item (has numPr in XML)."""
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    pPr = paragraph._element.find(f"{{{W}}}pPr")
    if pPr is not None:
        numPr = pPr.find(f"{{{W}}}numPr")
        if numPr is not None:
            return True
    return False
