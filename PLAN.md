# Build Plan - Legal Document Analyzer MCP Server

## Overview

Build a FastMCP server with 7 tools for analyzing Czech legal .docx documents.
Claude Code orchestrates the analysis and does semantic reasoning (redundancy, context).
Python tools handle deterministic checks (whitespace, enumerations, reference format).

## Build Phases

### Phase 1: Project Scaffolding
- [x] Initialize git repo
- [x] Create project structure (directories, __init__.py)
- [x] Create requirements.txt
- [x] Create .gitignore
- [x] Set up virtual environment and install dependencies

### Phase 2: Document Parser (`mcp_server/docx_parser.py`)
Core document parsing — everything else depends on this.
- [x] `_detect_heading_level(paragraph)` — detect heading level from style name + XML fallback
- [x] `load_document_structure(filepath)` — returns heading tree, paragraph count, flat heading list
- [x] `_build_heading_tree(headings)` — stack-based tree builder from flat heading list
- [x] `get_section_content(filepath, heading_text)` — full text under a specific heading
- [x] `get_all_sections_summary(filepath)` — compact summaries (200 chars + MD5 hash) per section
- [x] Manual test with a sample .docx

### Phase 3: MCP Server Skeleton (`mcp_server/server.py`)
- [x] Create FastMCP server instance
- [x] Register the 3 parser tools
- [x] Test that server starts and tools are callable
- [ ] Register with Claude Code (`claude mcp add`) — run manually (see below)
- [ ] Verify tools appear in Claude Code (`/mcp`)

### Phase 4: Whitespace Check (`mcp_server/checks.py`)
Simplest deterministic check — good first win.
- [ ] `check_whitespace(filepath)` — double spaces, trailing/leading whitespace, consecutive blanks
- [ ] Register in server.py
- [ ] Test with a document containing known whitespace issues

### Phase 5: Enumeration Check (`mcp_server/checks.py`)
Most complex deterministic check.
- [ ] `_get_numPr(paragraph)` — extract numId/ilvl from paragraph XML
- [ ] `_get_num_format(doc, numId, ilvl)` — get numbering format from definitions
- [ ] `_detect_text_list_pattern(text)` — regex detection of (a)/(b)/(i)/(ii) patterns
- [ ] `_check_list_delimiters(items)` — check delimiter consistency + last-item rules
- [ ] `check_enumerations(filepath)` — main function combining Word-native + text-pattern lists
- [ ] Register in server.py
- [ ] Test with document containing known enumeration issues

### Phase 6: Reference Extraction & Validation (`mcp_server/checks.py`)
- [ ] `_extract_field_codes(doc)` — walk XML for REF/PAGEREF field codes
- [ ] `_extract_text_references(doc)` — regex for Czech legal patterns (čl., bod, článek, odstavec, příloha, §)
- [ ] `_get_bookmarks(doc)` — extract all bookmarks for validation
- [ ] `_validate_references(refs, bookmarks, headings)` — check targets exist
- [ ] `extract_and_validate_references(filepath)` — main function combining all above
- [ ] Register in server.py
- [ ] Test with document containing cross-references

### Phase 7: Report Generation (`mcp_server/report.py`)
- [ ] `_generate_markdown(findings_data)` — structured markdown report by category
- [ ] `_generate_annotated_docx(filepath, findings_data, output_path)` — add comments to .docx copy
- [ ] `save_results(filepath, findings_json, output_path, format)` — main tool
- [ ] Register in server.py
- [ ] Test both output formats

### Phase 8: Integration & Testing
- [ ] End-to-end test with a real Czech legal document
- [ ] Test the full workflow: load → analyze → report
- [ ] Handle edge cases (empty doc, no headings, large doc)
- [ ] Fix any issues found

### Phase 9: Polish
- [ ] Improve CLAUDE.md with refined workflow instructions based on real usage
- [ ] Create a sample test document with known issues for demos
- [ ] Final commit and push

## Current Status

**Phase:** 2 complete, ready for Phase 3
**Last updated:** 2026-02-18
