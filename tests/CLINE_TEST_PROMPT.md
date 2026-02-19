# Cline MCP Test Prompt (Manual Evaluation)

**Goal:** Run the MCP tools on `documents/test_smlouva.docx` and compare your findings to the ground truth in `tests/ground_truth.py`.

## Instructions

1. **Load the document structure** and get summaries for all sections.
2. **Find redundant/near-duplicate sections** (including verbatim duplicates and near duplicates).
3. **Identify elaborations** (sections that expand on others and should NOT be flagged as redundant).
4. **Run whitespace checks** and list all whitespace issues.
5. **Attempt reference validation** and **enumeration checks** (expected to be incomplete, but try anyway).

## Output Requirements

- Provide a structured list of findings under headings:

  - `Redundancy (verbatim)`
  - `Redundancy (near-duplicate)`
  - `Elaboration (not redundant)`
  - `Whitespace`
  - `References`
  - `Enumerations`

- **Comparison vs Ground Truth:**
  - For each category, compare your results with `tests/ground_truth.py` and report:
    - **Found** = how many expected items you detected
    - **Expected** = how many items exist in ground truth
    - **Precision** = Found / Reported (if you reported extra items)
    - **Recall** = Found / Expected
    - **Percentage** for each (precision & recall as %)

Example:

```
Whitespace:
  Expected: 5
  Found: 4
  Reported: 4
  Precision: 100%
  Recall: 80%
```

If a category is not implemented yet (references/enumerations), clearly state:
"Not implemented — expected to fail" and still report **Expected** count from ground truth.

## Notes

- For redundancy, verbatim duplicates can be validated via matching content hashes.
- Near-duplicates require semantic judgment.
- Use the provided MCP tools only; do not assume missing tools exist.
