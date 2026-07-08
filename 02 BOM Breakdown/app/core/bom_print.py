from __future__ import annotations

import pandas as pd

from .lineage import refs_for_row
from .models import SectionPrint, WorkbookData
from .vba_compat import clean_text, get_version_label, sort_version_keys


DISPLAY_COLUMNS = ["Line No.", "Type", "No.", "Description", "Unit of Measure Code", "Quantity"]


def with_version_label(lines: pd.DataFrame) -> pd.DataFrame:
    out = lines.copy()
    out["__base_bom"] = out["Production BOM No."].map(clean_text)
    out["__version_label"] = out["Version Code"].map(get_version_label)
    return out


def build_version_dict(lines: pd.DataFrame, base_bom: str) -> list[str]:
    tagged = with_version_label(lines)
    labels = tagged.loc[tagged["__base_bom"].eq(clean_text(base_bom)), "__version_label"].tolist()
    return sort_version_keys(labels or ["V1"])


def find_bom_description(headers: pd.DataFrame, raw_bom: str, base_bom: str) -> str:
    wanted = {clean_text(raw_bom), clean_text(base_bom)}
    matched = headers[headers["No."].map(clean_text).isin(wanted)]
    if matched.empty:
        return ""
    return clean_text(matched.iloc[0].get("Description", ""))


def build_sections_print_all_bom(data: WorkbookData, selected_boms: list[str] | None = None) -> list[SectionPrint]:
    headers = data.headers
    lines = with_version_label(data.lines)
    selected = {clean_text(x) for x in selected_boms or [] if clean_text(x)}
    processed: set[str] = set()
    sections: list[SectionPrint] = []

    for _, header in headers.iterrows():
        base = clean_text(header.get("No."))
        if not base or (selected and base not in selected):
            continue
        labels = sort_version_keys(lines.loc[lines["__base_bom"].eq(base), "__version_label"].tolist() or ["V1"])
        for label in labels:
            key = f"{base}|{label}"
            if key in processed:
                continue
            processed.add(key)
            mask = lines["__base_bom"].eq(base) & lines["__version_label"].eq(label)
            detail = lines.loc[mask].copy()
            notes = []
            if detail.empty:
                notes.append("No detail rows were found in Production BOM Line.")
                rows = pd.DataFrame(columns=DISPLAY_COLUMNS)
                version_code = "" if label == "V1" else f"{base}-{label}"
                lineage_refs = []
            else:
                rows = detail[[c for c in DISPLAY_COLUMNS if c in detail.columns]].copy()
                version_code = clean_text(detail.iloc[0].get("Version Code", ""))
                lineage_refs = refs_for_row(
                    detail.iloc[0],
                    sheet="Production BOM Line",
                    headers=["Production BOM No.", "Version Code", "No.", "Quantity"],
                    column_maps=data.column_maps,
                    file_hash=data.file_hash,
                    parsed_at=data.parsed_at,
                )
            sections.append(
                SectionPrint(
                    base_bom=base,
                    version_label=label,
                    version_code=version_code,
                    description=clean_text(header.get("Description", "")),
                    rows=rows,
                    anchor_id=f"bom-{base}-{label}".replace(" ", "-"),
                    notes=notes,
                    lineage_refs=lineage_refs,
                )
            )
    return sections
