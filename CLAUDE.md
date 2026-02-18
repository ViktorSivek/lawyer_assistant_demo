# Legal Document Analyzer

## What We're Building

A custom MCP server that gives Claude Code the ability to analyze Czech legal .docx documents. Claude Code acts as both the orchestrator and the semantic AI engine. The MCP server provides tools for parsing .docx files and running deterministic checks.

## Architecture

```
User → Claude Code (AI orchestrator + semantic reasoning)
                ↓ calls MCP tools
         FastMCP Python Server (stdio)
                ↓ uses
         python-docx + lxml + regex
                ↓ outputs
         Markdown report + annotated .docx with comments
```

## What the Lawyer Needs

1. **Redundancy detection**: Find sections that are contextually redundant (mentioned twice)
2. **Section relationships**: Identify if one section just elaborates another (e.g., annex deepening a general clause)
3. **Cross-reference validation**: Validate all references contextually (not just existence)
4. **Reference format check**: Ensure references use Word field codes (not plain text)
5. **Whitespace check**: Find all extra/redundant whitespace
6. **Enumeration consistency**: Check (a)/(b)/(c) and (i)/(ii)/(iii) delimiter consistency

## Project Structure

```
lawyer_assistant_demo/
├── CLAUDE.md                  # This file - project context
├── PLAN.md                    # Build plan with checklist
├── mcp_server/
│   ├── __init__.py
│   ├── server.py              # FastMCP server, 7 tool registrations
│   ├── docx_parser.py         # Document parsing, heading tree, sections
│   ├── checks.py              # Whitespace, enumerations, references
│   └── report.py              # Markdown report + annotated .docx output
├── documents/                 # Place .docx files here
├── output/                    # Reports go here
├── tests/
│   └── test_tools.py          # Unit tests
├── requirements.txt
└── .gitignore
```

## MCP Tools (7 total)

| # | Tool | Purpose |
|---|------|---------|
| 1 | `load_document_structure` | Parse .docx heading tree + metadata |
| 2 | `get_section_content` | Get full text under a specific heading |
| 3 | `get_all_sections_summary` | Compact section previews for redundancy screening |
| 4 | `check_whitespace` | Deterministic: double spaces, trailing/leading whitespace |
| 5 | `check_enumerations` | Deterministic: enumeration delimiter consistency |
| 6 | `extract_and_validate_references` | Extract field-code + text refs, validate targets |
| 7 | `save_results` | Generate markdown report or annotated .docx |

## Analysis Workflow

When asked to analyze a document:
1. Call `load_document_structure` to understand organization
2. Call `get_all_sections_summary` to screen for redundancy candidates
3. Call `get_section_content` for candidate pairs, reason about redundancy vs elaboration
4. Call `extract_and_validate_references`, reason about contextual validity
5. Call `check_whitespace` and `check_enumerations` for deterministic checks
6. Call `save_results` to output markdown report + annotated .docx

## Tech Stack

- Python 3.10+
- FastMCP (MCP server framework)
- python-docx (parse/write .docx)
- lxml (XML manipulation for field codes)
- No OS-specific dependencies — works on Windows, Linux, WSL
