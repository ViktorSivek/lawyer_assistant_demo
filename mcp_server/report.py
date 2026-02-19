"""Report generation — markdown summary and annotated .docx output."""

from __future__ import annotations

import json
import os
import zipfile
from collections import defaultdict
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_COMMENT_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument"
    ".wordprocessingml.comments+xml"
)
_COMMENT_REL_TYPE = (
    "http://schemas.openxmlformats.org/officeDocument"
    "/2006/relationships/comments"
)
_RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


# ── markdown ────────────────────────────────────────────────────────


def _generate_markdown(findings: dict[str, Any]) -> str:
    """Render a structured Czech-language markdown report from findings."""
    filepath = findings.get("filepath", "")
    filename = Path(filepath).name if filepath else "?"
    today = date.today().strftime("%Y-%m-%d")

    ws = findings.get("whitespace", {})
    en = findings.get("enumerations", {})
    refs = findings.get("references", {})

    ws_count = ws.get("issue_count", 0)
    en_count = en.get("issue_count", 0)
    inv_count = len(refs.get("invalid", []))
    fv_count = len(refs.get("field_code_violations", []))
    total = ws_count + en_count + inv_count + fv_count

    lines: list[str] = [
        f"# Analýza dokumentu: {filename}",
        "",
        f"**Datum analýzy:** {today}  ",
        f"**Soubor:** `{filepath}`",
        "",
        "## Souhrn",
        "",
        "| Kategorie | Počet nálezů |",
        "|---|---|",
        f"| Bílé znaky | {ws_count} |",
        f"| Enumerace | {en_count} |",
        f"| Neplatné reference | {inv_count} |",
        f"| Chybějící pole (field codes) | {fv_count} |",
        f"| **Celkem** | **{total}** |",
        "",
    ]

    # ── whitespace ──
    if ws_count:
        lines += ["## Bílé znaky", ""]
        for issue in ws.get("issues", []):
            lines.append(
                f"- **{issue.get('type', '?')}** "
                f"(odst. {issue.get('paragraph_index', '?')}, "
                f"sekce: _{issue.get('section', '?')}_)  "
            )
            lines.append(f"  `{issue.get('detail', '')}`")
        lines.append("")

    # ── enumerations ──
    if en_count:
        lines += ["## Enumerace", ""]
        for issue in en.get("issues", []):
            lines.append(
                f"- **{issue.get('type', '?')}** "
                f"(odst. {issue.get('paragraph_index', '?')}, "
                f"sekce: _{issue.get('section', '?')}_)  "
            )
            lines.append(f"  `{issue.get('detail', '')}`")
        lines.append("")

    # ── invalid references ──
    if inv_count:
        lines += ["## Neplatné reference", ""]
        for ref in refs.get("invalid", []):
            lines.append(
                f"- **{ref.get('text', '?')}** "
                f"(sekce: _{ref.get('section', '?')}_) — cíl nenalezen"
            )
        lines.append("")

    # ── field code violations ──
    if fv_count:
        lines += [
            "## Chybějící pole (field codes)",
            "",
            "Následující reference jsou zapsány jako prostý text místo Word polí (REF):",
            "",
        ]
        by_section: dict[str, list[str]] = defaultdict(list)
        for ref in refs.get("field_code_violations", []):
            by_section[ref.get("section", "Neznámá sekce")].append(
                ref.get("text", "?")
            )
        for sec, texts in by_section.items():
            lines.append(f"- _{sec}_: {', '.join(sorted(set(texts)))}")
        lines.append("")

    return "\n".join(lines)


# ── annotated docx ──────────────────────────────────────────────────


def _generate_annotated_docx(
    filepath: str,
    annotations: list[dict[str, Any]],
    output_path: str,
) -> None:
    """Write a copy of *filepath* to *output_path* with Word comments injected.

    annotations: list of {paragraph_index, comment, category}
    Comments for the same paragraph are merged into one.
    """
    with zipfile.ZipFile(filepath, "r") as zin:
        file_list = zin.namelist()
        content_map: dict[str, bytes] = {n: zin.read(n) for n in file_list}

    if not annotations:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(content_map.get("", b""))
        import shutil
        shutil.copy2(filepath, output_path)
        return

    # ── parse document.xml ──
    doc_root = etree.fromstring(content_map["word/document.xml"])
    all_paras = list(doc_root.iter(f"{{{W}}}p"))

    # Group annotations by paragraph index
    by_para: dict[int, list[dict]] = defaultdict(list)
    for ann in annotations:
        idx = ann["paragraph_index"]
        if 0 <= idx < len(all_paras):
            by_para[idx].append(ann)

    # ── build comments.xml ──
    date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    comments_root = etree.Element(f"{{{W}}}comments")
    comment_id = 0

    for para_idx in sorted(by_para):
        anns = by_para[para_idx]
        combined = "\n".join(
            f"[{a.get('category', 'issue').upper()}] {a['comment']}"
            for a in anns
        )
        para_el = all_paras[para_idx]

        # Build <w:comment> element
        c = etree.SubElement(comments_root, f"{{{W}}}comment")
        c.set(f"{{{W}}}id", str(comment_id))
        c.set(f"{{{W}}}author", "Legal Analyzer")
        c.set(f"{{{W}}}date", date_str)
        c.set(f"{{{W}}}initials", "LA")
        p_el = etree.SubElement(c, f"{{{W}}}p")
        r_el = etree.SubElement(p_el, f"{{{W}}}r")
        t_el = etree.SubElement(r_el, f"{{{W}}}t")
        t_el.text = combined
        t_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

        # Inject markers into the target paragraph
        start = etree.Element(f"{{{W}}}commentRangeStart")
        start.set(f"{{{W}}}id", str(comment_id))

        end = etree.Element(f"{{{W}}}commentRangeEnd")
        end.set(f"{{{W}}}id", str(comment_id))

        ref_run = etree.Element(f"{{{W}}}r")
        rpr = etree.SubElement(ref_run, f"{{{W}}}rPr")
        rs = etree.SubElement(rpr, f"{{{W}}}rStyle")
        rs.set(f"{{{W}}}val", "CommentReference")
        ref_el = etree.SubElement(ref_run, f"{{{W}}}commentReference")
        ref_el.set(f"{{{W}}}id", str(comment_id))

        # Insert start after <w:pPr> if present, else at position 0
        insert_pos = 0
        for i, child in enumerate(para_el):
            if child.tag == f"{{{W}}}pPr":
                insert_pos = i + 1
                break
        para_el.insert(insert_pos, start)
        para_el.append(end)
        para_el.append(ref_run)

        comment_id += 1

    # ── serialize modified parts ──
    modified_doc = etree.tostring(
        doc_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    comments_xml = etree.tostring(
        comments_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    # ── update _rels ──
    rels_key = "word/_rels/document.xml.rels"
    rels_root = etree.fromstring(content_map[rels_key])
    if not any(el.get("Type") == _COMMENT_REL_TYPE for el in rels_root):
        existing_ids = [el.get("Id", "") for el in rels_root]
        next_num = (
            max(
                (int(i[3:]) for i in existing_ids if i.startswith("rId") and i[3:].isdigit()),
                default=0,
            )
            + 1
        )
        rel = etree.SubElement(rels_root, f"{{{_RELS_NS}}}Relationship")
        rel.set("Id", f"rId{next_num}")
        rel.set("Type", _COMMENT_REL_TYPE)
        rel.set("Target", "comments.xml")
    modified_rels = etree.tostring(
        rels_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    # ── update [Content_Types].xml ──
    ct_root = etree.fromstring(content_map["[Content_Types].xml"])
    if not any(el.get("PartName") == "/word/comments.xml" for el in ct_root):
        override = etree.SubElement(ct_root, f"{{{_CT_NS}}}Override")
        override.set("PartName", "/word/comments.xml")
        override.set("ContentType", _COMMENT_CONTENT_TYPE)
    modified_ct = etree.tostring(
        ct_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    # ── write new zip ──
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in file_list:
            if name == "word/document.xml":
                zout.writestr(name, modified_doc)
            elif name == rels_key:
                zout.writestr(name, modified_rels)
            elif name == "[Content_Types].xml":
                zout.writestr(name, modified_ct)
            else:
                zout.writestr(name, content_map[name])
        zout.writestr("word/comments.xml", comments_xml)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_bytes(buf.getvalue())


# ── public API ──────────────────────────────────────────────────────


def save_results(
    filepath: str,
    findings_json: str,
    output_path: str,
    format: str = "markdown",
) -> dict[str, Any]:
    """Generate a report from analysis findings.

    Args:
        filepath:      Original .docx file path.
        findings_json: JSON string with keys: whitespace, enumerations,
                       references (results from the check tools).
        output_path:   Destination file path (.md or .docx).
        format:        "markdown" (default) or "docx".

    Returns:
        {output_path, format, written_bytes, summary}
    """
    if not os.path.isfile(filepath):
        return {"error": f"File not found: {filepath}"}

    try:
        findings: dict[str, Any] = json.loads(findings_json)
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid findings_json: {exc}"}

    findings["filepath"] = filepath

    if format == "docx":
        annotations: list[dict[str, Any]] = []

        for issue in findings.get("whitespace", {}).get("issues", []):
            annotations.append({
                "paragraph_index": issue["paragraph_index"],
                "comment": issue["detail"],
                "category": "whitespace",
            })
        for issue in findings.get("enumerations", {}).get("issues", []):
            annotations.append({
                "paragraph_index": issue["paragraph_index"],
                "comment": issue["detail"],
                "category": "enumeration",
            })
        for ref in findings.get("references", {}).get("invalid", []):
            annotations.append({
                "paragraph_index": ref["paragraph_index"],
                "comment": f"Neplatná reference: {ref['text']} — cíl nenalezen",
                "category": "reference",
            })

        _generate_annotated_docx(filepath, annotations, output_path)

    else:  # markdown
        md = _generate_markdown(findings)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(md, encoding="utf-8")

    written = Path(output_path).stat().st_size

    return {
        "output_path": output_path,
        "format": format,
        "written_bytes": written,
        "summary": {
            "whitespace_issues": findings.get("whitespace", {}).get("issue_count", 0),
            "enumeration_issues": findings.get("enumerations", {}).get("issue_count", 0),
            "invalid_refs": len(findings.get("references", {}).get("invalid", [])),
            "field_code_violations": len(
                findings.get("references", {}).get("field_code_violations", [])
            ),
        },
    }
