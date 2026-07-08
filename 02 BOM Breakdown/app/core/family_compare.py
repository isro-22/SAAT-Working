from __future__ import annotations

import pandas as pd

from .bom_print import with_version_label
from .models import WorkbookData
from .vba_compat import clean_text, line_sort_value, normalize_component_key


BASE_FIELDS = ["Line No.", "Type", "No.", "Description", "Unit of Measure Code"]


def build_family_matrix(data: WorkbookData, family_name: str, include_all_versions: bool = True) -> pd.DataFrame:
    cf = data.cf[data.cf["Family Name"].map(clean_text).eq(clean_text(family_name))]
    lines = with_version_label(data.lines)
    records: dict[str, dict] = {}

    for _, cf_row in cf.iterrows():
        item_code = clean_text(cf_row.get("Item Code"))
        subset = lines[lines["__base_bom"].eq(item_code)]
        if not include_all_versions:
            subset = subset[subset["__version_label"].eq("V1")]
        seen: dict[str, int] = {}
        for _, line in subset.iterrows():
            raw_key = normalize_component_key(line.get("Type"), line.get("No."))
            seen[raw_key] = seen.get(raw_key, 0) + 1
            key = normalize_component_key(line.get("Type"), line.get("No."), seen[raw_key] - 1)
            rec = records.setdefault(key, {field: line.get(field, "") for field in BASE_FIELDS})
            col = f"{item_code}|{line.get('__version_label')} Qty"
            rec[col] = line.get("Quantity", "")

    matrix = pd.DataFrame(records.values())
    if matrix.empty:
        return matrix
    matrix["__sort"] = matrix["Line No."].map(line_sort_value)
    matrix = matrix.sort_values("__sort").drop(columns=["__sort"]).reset_index(drop=True)
    return matrix
