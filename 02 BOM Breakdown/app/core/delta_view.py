from __future__ import annotations

import pandas as pd

from .bom_print import with_version_label
from .models import DeltaResult
from .vba_compat import clean_text, normalize_component_key


COMPARE_FIELDS = ["Type", "No.", "Description", "Unit of Measure Code", "Quantity"]


def _component_map(lines: pd.DataFrame, base_bom: str, version_label: str) -> dict[str, dict]:
    tagged = with_version_label(lines)
    subset = tagged[tagged["__base_bom"].map(clean_text).eq(clean_text(base_bom)) & tagged["__version_label"].eq(version_label)]
    result: dict[str, dict] = {}
    seen: dict[str, int] = {}
    for _, row in subset.iterrows():
        raw_key = normalize_component_key(row.get("Type"), row.get("No."))
        seen[raw_key] = seen.get(raw_key, 0) + 1
        key = normalize_component_key(row.get("Type"), row.get("No."), seen[raw_key] - 1)
        result[key] = {field: row.get(field, "") for field in COMPARE_FIELDS}
        result[key]["Line No."] = row.get("Line No.", "")
    return result


def build_delta_view(lines: pd.DataFrame, base_bom: str, v_old: str, v_new: str) -> DeltaResult:
    old = _component_map(lines, base_bom, v_old)
    new = _component_map(lines, base_bom, v_new)
    old_keys = set(old)
    new_keys = set(new)
    added = [{"key": key, **new[key]} for key in sorted(new_keys - old_keys)]
    removed = [{"key": key, **old[key]} for key in sorted(old_keys - new_keys)]
    changed = []
    for key in sorted(old_keys & new_keys):
        for field in COMPARE_FIELDS:
            if clean_text(old[key].get(field)) != clean_text(new[key].get(field)):
                changed.append({"key": key, "field": field, "from": old[key].get(field), "to": new[key].get(field)})
    return DeltaResult(base_bom=base_bom, v_old=v_old, v_new=v_new, added=added, removed=removed, changed=changed)
