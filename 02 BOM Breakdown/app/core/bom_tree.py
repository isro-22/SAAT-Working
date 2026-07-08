from __future__ import annotations

from typing import Any

import pandas as pd

from .bom_print import with_version_label
from .models import WorkbookData
from .vba_compat import clean_text, line_sort_value


TREE_COLUMNS = [
    "Level",
    "Tree",
    "Parent BOM",
    "Parent Version",
    "Seq",
    "Line No.",
    "Type",
    "Component No.",
    "Description",
    "UoM",
    "Quantity",
    "Cumulative Qty",
    "Is Sub-BOM",
    "Path",
]


def _to_float(value: object, default: float = 1.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _version_subset(lines: pd.DataFrame, bom_no: str, version_label: str) -> tuple[pd.DataFrame, str]:
    bom = clean_text(bom_no)
    wanted = clean_text(version_label) or "V1"
    subset = lines[lines["__base_bom"].eq(bom) & lines["__version_label"].eq(wanted)].copy()
    if subset.empty and wanted != "V1":
        subset = lines[lines["__base_bom"].eq(bom) & lines["__version_label"].eq("V1")].copy()
        return subset, "V1"
    return subset, wanted


def build_bom_tree(
    data: WorkbookData,
    base_bom: str,
    version_label: str = "V1",
    max_depth: int = 4,
    type_filter: list[str] | None = None,
    expand_only_bom: bool = True,
) -> pd.DataFrame:
    lines = with_version_label(data.lines)
    available_boms = set(lines["__base_bom"].map(clean_text))
    type_set = {clean_text(value) for value in type_filter or [] if clean_text(value)}
    root = clean_text(base_bom)
    rows: list[dict[str, Any]] = []

    def walk(parent_bom: str, parent_version: str, level: int, path: list[str], cumulative_qty: float) -> None:
        if level > max_depth:
            return
        subset, actual_version = _version_subset(lines, parent_bom, parent_version)
        if subset.empty:
            return
        subset["__sort"] = subset["Line No."].map(line_sort_value)
        subset = subset.sort_values("__sort")
        for sibling_index, (_, line) in enumerate(subset.iterrows(), start=1):
            component_no = clean_text(line.get("No."))
            component_type = clean_text(line.get("Type"))
            if type_set and component_type not in type_set:
                continue
            qty = _to_float(line.get("Quantity"))
            child_is_bom = component_no in available_boms
            child_path = [*path, component_no or "(blank)"]
            rows.append(
                {
                    "Level": level,
                    "Tree": f"{'   ' * (level - 1)}{'▸' if child_is_bom else '•'} {component_no}",
                    "Parent BOM": parent_bom,
                    "Parent Version": actual_version,
                    "Seq": sibling_index,
                    "Line No.": line.get("Line No.", ""),
                    "Type": component_type,
                    "Component No.": component_no,
                    "Description": clean_text(line.get("Description")),
                    "UoM": clean_text(line.get("Unit of Measure Code")),
                    "Quantity": line.get("Quantity", ""),
                    "Cumulative Qty": cumulative_qty * qty,
                    "Is Sub-BOM": child_is_bom,
                    "Path": " > ".join(child_path),
                }
            )
            if child_is_bom and level < max_depth and component_no not in path:
                walk(component_no, actual_version, level + 1, child_path, cumulative_qty * qty)
            elif not expand_only_bom and level < max_depth and component_no not in path:
                walk(component_no, actual_version, level + 1, child_path, cumulative_qty * qty)

    walk(root, version_label, 1, [root], 1.0)
    if not rows:
        return pd.DataFrame(columns=TREE_COLUMNS)
    return pd.DataFrame(rows, columns=TREE_COLUMNS)
