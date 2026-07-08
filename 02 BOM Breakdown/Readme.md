# Production BOM Analyzer

A Python Streamlit application for analyzing Production BOM workbooks exported from ERP/Excel. The app reads `Production BOM Header`, `Production BOM Line`, and `CF List`, then generates reusable analysis data once so users can explore BOM sections, CF mappings, family comparisons, BOM trees, and version deltas without repeatedly rebuilding the workbook.

## Current Features

- Excel import with dynamic header detection.
- Required sheet validation for:
  - `Production BOM Header`
  - `Production BOM Line`
  - `CF List`
- VBA-compatible helpers for text cleanup, BOM version detection, component keys, version sorting, and line sorting.
- Generate-once workflow:
  - Parse workbook.
  - Build quality summary.
  - Build `PRINT_ALL_BOM` sections.
  - Build CF-to-BOM mapping.
  - Store generated analysis in Streamlit session/cache for faster viewing.
- Apple-like overview dashboard.
- `PRINT_ALL_BOM` section viewer by Base BOM and version.
- CF Explorer with detail links that open a focused BOM detail page in a new browser tab.
- Family Comparison with yellow quantity-difference highlighting.
- Export all family comparison sheets to XLSX.
- BOM Tree with simple expand/collapse controls by BOM level.
- Delta View for added, removed, and changed components across versions.
- JSON/CSV exports for tree and delta outputs.
- Basic lineage references for section rows.

## Workbook Expectations

The workbook must contain these sheets:

| Sheet | Purpose |
| --- | --- |
| `Production BOM Header` | BOM master/header data |
| `Production BOM Line` | BOM component lines and version codes |
| `CF List` | CF item list and family mapping |

The sample workbook in this workspace is:

```text
Export BOM.xlsx
```

The app automatically uses that file when no upload is provided.

## Project Structure

```text
.
├── app/
│   ├── main.py                    # Streamlit UI and page flow
│   └── core/
│       ├── bom_print.py           # PRINT_ALL_BOM section builder
│       ├── bom_tree.py            # Expandable BOM tree builder
│       ├── cf_builder.py          # CF List mapping and detail anchors
│       ├── delta_view.py          # Version delta calculations
│       ├── excel_io.py            # Workbook parsing and validation
│       ├── family_compare.py      # Normalized family comparison matrix
│       ├── family_export.py       # XLSX export with highlighted changes
│       ├── graph_builder.py       # Delta graph helper
│       ├── lineage.py             # Lineage reference helpers
│       ├── models.py              # Dataclasses used across the app
│       └── vba_compat.py          # VBA-compatible normalization/version helpers
├── assets/                        # Static UI assets, if needed later
├── data/                          # Optional place for sample workbooks
├── docs/                          # Additional design or release notes
├── tests/
│   └── unit/
│       └── test_vba_compat.py
├── Export BOM.xlsx                # Current sample workbook
├── requirements.txt
└── Readme.md
```

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run the app:

```bash
.venv/bin/streamlit run app/main.py
```

Open:

```text
http://localhost:8501
```

## Usage

1. Open the app.
2. Use the local `Export BOM.xlsx` file or upload another workbook.
3. Click `Generate Analysis`.
4. Use the tabs:
   - `Overview`
   - `PRINT_ALL_BOM`
   - `CF Explorer`
   - `Family Comparison`
   - `BOM Tree`
   - `Delta View`
   - `Utilities`

## BOM Tree Behavior

The BOM Tree tab is designed as a simple expandable outline:

- `L1`, `L2`, `L3`, etc. show the BOM level.
- `Sub-BOM` means the component also has a BOM and can be expanded.
- `Leaf` means the component has no child BOM in the workbook.
- `No: 1, 2, 3...` is a sibling sequence number generated for readability.
- The original ERP `Line No.` remains available in the table/export data.

## Development Notes

- Keep workbook parsing and business logic inside `app/core/`.
- Keep Streamlit layout and interaction logic inside `app/main.py`.
- Prefer generated analysis/cache for expensive operations.
- Avoid rebuilding all sections on every UI interaction.
- Add unit tests for normalization, version parsing, tree building, and delta behavior when logic changes.

## Verification

Run tests:

```bash
.venv/bin/python -m pytest -q
```

Compile-check the app:

```bash
.venv/bin/python -m py_compile app/main.py app/core/*.py
```

## Known Scope

Implemented:

- Parsing and validation.
- Generate-once analysis flow.
- PRINT_ALL_BOM sections.
- CF detail links.
- Family comparison and XLSX export.
- Expandable BOM Tree.
- Delta View.

Future improvements:

- Full lineage lookup UI by cell.
- PDF/HTML export.
- Custom validation rule editor.
- Larger workbook performance profiling.
- End-to-end UI tests.
