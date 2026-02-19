# Legal Document Analyzer

An MCP server that gives AI assistants (Claude Code, Cursor, etc.) the ability to analyze Czech legal `.docx` contracts. The server provides tools for parsing document structure, detecting whitespace issues, validating cross-references, and checking enumeration consistency. The AI assistant acts as the orchestrator — it calls the tools and does the semantic reasoning (redundancy detection, contextual validation).

## How It Works

```
You → AI assistant (Claude Code / Cursor / etc.)
              ↓ calls MCP tools
       FastMCP Python Server (stdio transport)
              ↓ uses
       python-docx + lxml + regex
              ↓ finds
       Whitespace issues, bad references, inconsistent enumerations, redundant sections
```

The server handles deterministic checks (whitespace, enumerations, reference format). The AI handles semantic analysis (is this section truly redundant, or just an elaboration?).

## What It Detects

| Category | How | Examples |
|---|---|---|
| **Redundancy** | AI reasoning over section summaries | Verbatim duplicates, near-duplicate clauses, elaboration vs repetition |
| **Cross-references** | Deterministic + AI | Invalid refs (článek 12 doesn't exist), plain-text refs that should be field codes |
| **Whitespace** | Deterministic | Double spaces, trailing/leading whitespace, consecutive blank paragraphs |
| **Enumerations** | Deterministic | Mixed delimiters in (a)/(b)/(c) lists, missing periods on last items |

## Setup

### 1. Clone and install

```bash
git clone https://github.com/ViktorSivek/lawyer_assistant_demo.git
cd lawyer_assistant_demo
python -m venv .venv
source .venv/bin/activate        # Linux/macOS/WSL
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 2. Add the MCP server to your AI client

**Claude Code:**

```bash
claude mcp add legal-analyzer -- /absolute/path/to/lawyer_assistant_demo/.venv/bin/python /absolute/path/to/lawyer_assistant_demo/mcp_server/server.py
```

Example with real paths:

```bash
# Linux / WSL
claude mcp add legal-analyzer -- /home/viktor/Projects/lawyer_assistant_demo/.venv/bin/python /home/viktor/Projects/lawyer_assistant_demo/mcp_server/server.py

# Windows
claude mcp add legal-analyzer -- C:\Users\viktor\Projects\lawyer_assistant_demo\.venv\Scripts\python.exe C:\Users\viktor\Projects\lawyer_assistant_demo\mcp_server\server.py
```

Verify it's registered:

```bash
claude mcp list
```

Then inside Claude Code, run `/mcp` to confirm the tools appear.

**Cursor / other MCP clients:**

Add to your MCP config file (e.g. `.cursor/mcp.json` or `mcp_settings.json`):

```json
{
  "mcpServers": {
    "legal-analyzer": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/mcp_server/server.py"]
    }
  }
}
```

### 3. Analyze a document

Place your `.docx` file in the `documents/` folder, then ask your AI assistant:

> Analyze the document at documents/my_contract.docx

The AI will call the MCP tools automatically and produce a structured analysis.

## MCP Tools

| Tool | What it does |
|------|-------------|
| `tool_load_document_structure` | Parse heading tree, paragraph count, metadata |
| `tool_get_section_content` | Get full text under a specific heading |
| `tool_get_all_sections_summary` | Compact preview + content hash per section (for redundancy screening) |
| `tool_check_whitespace` | Find double spaces, trailing/leading whitespace, consecutive blanks |
| `tool_check_enumerations` | Check (a)/(b)/(c) and (i)/(ii)/(iii) delimiter consistency |
| `tool_extract_and_validate_references` | Extract field-code + text refs, validate targets exist |
| `tool_save_results` | Generate markdown report or annotated .docx with comments |

## Running Tests

```bash
source .venv/bin/activate
pip install pytest
python -m pytest tests/test_tools.py -v
```

To regenerate the test document (a synthetic Czech construction contract with embedded issues):

```bash
python tests/generate_test_doc.py
```

## Project Structure

```
lawyer_assistant_demo/
├── mcp_server/
│   ├── server.py          # FastMCP server + tool registrations
│   ├── docx_parser.py     # Document parsing, heading tree, sections
│   ├── checks.py          # Whitespace, enumerations, references
│   └── report.py          # Markdown + annotated .docx output
├── documents/             # Place .docx files here
├── output/                # Generated reports go here
├── tests/
│   ├── test_tools.py      # Automated tests (pytest)
│   ├── generate_test_doc.py  # Generates test_smlouva.docx
│   └── ground_truth.py    # Expected findings for test document
├── CLAUDE.md              # Workflow instructions for Claude Code
├── PLAN.md                # Build plan with progress tracking
└── requirements.txt       # fastmcp, python-docx, lxml
```

## Tech Stack

- **Python 3.10+** — no OS-specific dependencies, works on Windows, Linux, WSL
- **FastMCP** — MCP server framework (stdio transport)
- **python-docx** — parse and write .docx files (including adding comments)
- **lxml** — XML manipulation for field codes and numbering definitions
