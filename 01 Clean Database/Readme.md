# Clean Database

Streamlit app to validate and consolidate `data/Bahan.xlsx` into a clean BOL x SAAT output workbook.

## What it does

- Validates item codes from `01 BOL DB` and `02 SAAT BIN`
- Flags code status as valid, hidden-space valid, invalid format, empty, or Excel formula error
- Shows a live summary of valid `GEN-XXX-00000` segments
- Builds a merged master list with SAAT/BOL markers
- Supports manual curation for `SAAT Only` rows through a dropdown or manual input
- Converts SAAT IDR/kg values into USD/kg using the exchange rate in the sidebar
- Exports the final workbook as `BOL-SAAT List.xlsx`

## Current UI

- Apple-like, clean, scientific layout
- Sidebar upload panel
- Green/red status pills for required sheets
- Template download button for upload preparation
- Manual matching section before final generation

## Required sheets

The workbook must contain these sheets:

- `01 BOL DB`
- `01 SAAT DB`
- `02 SAAT BIN`

## How to use

1. Download the upload template from the sidebar.
2. Fill your workbook using the expected sheet structure.
3. Upload the file in the app.
4. Confirm the sheet status indicators turn green.
5. Fill manual chemical mapping for `SAAT Only` rows if needed.
6. Click `Generate Final Output`.
7. Download the final Excel file.

## Key output columns

- `Item Code`
- `SAAT`
- `BOL`
- `Jumlah *`
- `Item Name`
- `Chemical Name`
- `Price (USD)/KG`
- `CAS Number`
- `Appearance`

## Files in this folder

- `app.py` - Streamlit app
- `src/ui_theme.py` - shared CSS and sheet-status UI helpers
- `data/Bahan.xlsx` - sample source workbook
- `data/output.xlsx` - example output workbook

## Suggested structure

The app is intentionally lean, but the current folder layout is ready for future growth:

- `app.py` for the Streamlit entry point
- `src/` for reusable app modules
- `data/` for source workbooks, examples, and exports
- `Readme.md` for operating notes and setup guidance

## Run locally

```bash
streamlit run app.py
```
