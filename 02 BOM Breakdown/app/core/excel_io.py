from __future__ import annotations

import hashlib
from io import BytesIO
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from .models import WorkbookData
from .vba_compat import clean_text


REQUIRED_SHEETS = ["Production BOM Header", "Production BOM Line", "CF List"]
REQUIRED_COLUMNS = {
    "Production BOM Header": ["No.", "Description", "Unit of Measure Code", "Creation Date", "Status"],
    "Production BOM Line": [
        "Production BOM No.",
        "Version Code",
        "Line No.",
        "Type",
        "No.",
        "Description",
        "Unit of Measure Code",
        "Quantity",
    ],
    "CF List": ["Item Code", "Item Name", "Type", "Family Name"],
}


def _read_bytes(source: str | Path | bytes | BinaryIO) -> bytes:
    if isinstance(source, bytes):
        return source
    if hasattr(source, "getvalue"):
        return source.getvalue()
    if hasattr(source, "read"):
        pos = source.tell()
        data = source.read()
        source.seek(pos)
        return data
    return Path(source).read_bytes()


def file_hash(source: str | Path | bytes | BinaryIO) -> str:
    return hashlib.sha256(_read_bytes(source)).hexdigest()


def detect_header_row(raw: pd.DataFrame, required: list[str], scan_rows: int = 30) -> int:
    required_norm = {clean_text(x).casefold() for x in required}
    best_score = -1
    best_row = 0
    for idx in range(min(scan_rows, len(raw))):
        values = {clean_text(x).casefold() for x in raw.iloc[idx].tolist() if clean_text(x)}
        score = len(required_norm & values)
        if score > best_score:
            best_score = score
            best_row = idx
    if best_score < len(required_norm):
        missing = sorted(required_norm - {clean_text(x).casefold() for x in raw.iloc[best_row].tolist()})
        raise ValueError(f"Required header columns are incomplete. Missing: {missing}")
    return best_row + 1


def load_excel(source: str | Path | bytes | BinaryIO) -> WorkbookData:
    digest = file_hash(source)
    parsed_at = datetime.now()
    excel_source = BytesIO(source) if isinstance(source, bytes) else source
    excel = pd.ExcelFile(excel_source, engine="openpyxl")
    missing_sheets = [sheet for sheet in REQUIRED_SHEETS if sheet not in excel.sheet_names]
    if missing_sheets:
        raise ValueError(f"Required sheets were not found: {', '.join(missing_sheets)}")

    frames: dict[str, pd.DataFrame] = {}
    header_rows: dict[str, int] = {}
    column_maps: dict[str, dict[str, int]] = {}
    warnings: list[str] = []

    for sheet in REQUIRED_SHEETS:
        raw = pd.read_excel(excel, sheet_name=sheet, header=None, dtype=object)
        header_row = detect_header_row(raw, REQUIRED_COLUMNS[sheet])
        df = pd.read_excel(excel, sheet_name=sheet, header=header_row - 1, dtype=object)
        df.columns = [clean_text(c) or f"Unnamed {i + 1}" for i, c in enumerate(df.columns)]
        df = df.dropna(how="all").copy()
        df["__source_row"] = [header_row + 1 + i for i in range(len(df))]
        frames[sheet] = df
        header_rows[sheet] = header_row
        column_maps[sheet] = {clean_text(c): i + 1 for i, c in enumerate(df.columns) if not str(c).startswith("__")}

    header_nos = set(frames["Production BOM Header"]["No."].map(clean_text))
    line_boms = set(frames["Production BOM Line"]["Production BOM No."].map(clean_text))
    line_without_header = sorted(x for x in line_boms if x and x not in header_nos)
    header_without_line = sorted(x for x in header_nos if x and x not in line_boms)
    if line_without_header:
        warnings.append(f"{len(line_without_header)} BOM Line records do not have a matching Header.")
    if header_without_line:
        warnings.append(f"{len(header_without_line)} BOM Header records do not have matching Lines.")

    return WorkbookData(
        headers=frames["Production BOM Header"],
        lines=frames["Production BOM Line"],
        cf=frames["CF List"],
        file_hash=digest,
        parsed_at=parsed_at,
        header_rows=header_rows,
        column_maps=column_maps,
        warnings=warnings,
    )


def quality_summary(data: WorkbookData) -> dict[str, int]:
    lines = data.lines
    headers = data.headers
    qty = pd.to_numeric(lines["Quantity"], errors="coerce")
    return {
        "cf_items": int(len(data.cf)),
        "bom_headers": int(len(headers)),
        "bom_lines": int(len(lines)),
        "unique_line_boms": int(lines["Production BOM No."].map(clean_text).nunique()),
        "header_duplicates": int(headers["No."].map(clean_text).duplicated().sum()),
        "quantity_zero_or_negative": int((qty <= 0).fillna(True).sum()),
        "blank_line_uom": int(lines["Unit of Measure Code"].map(clean_text).eq("").sum()),
        "blank_line_description": int(lines["Description"].map(clean_text).eq("").sum()),
    }
