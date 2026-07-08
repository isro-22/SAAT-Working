from __future__ import annotations

from .bom_print import build_sections_print_all_bom, build_version_dict
from .models import CFEntry, SectionPrint, WorkbookData
from .vba_compat import clean_text, get_base_bom, get_version_label, has_version_suffix


IGNORE_CF_VALUES = {"", "NO", "BOM NO", "BOM NO.", "ITEM CODE", "ITEM NO", "N/A", "-"}


def build_sections_from_cf(data: WorkbookData) -> tuple[list[CFEntry], list[SectionPrint]]:
    sections = build_sections_print_all_bom(data)
    section_map = {(s.base_bom, s.version_label): s.anchor_id for s in sections}
    entries: list[CFEntry] = []

    for _, row in data.cf.iterrows():
        code = clean_text(row.get("Item Code"))
        if clean_text(code).upper() in IGNORE_CF_VALUES:
            continue
        base = get_base_bom(code)
        if has_version_suffix(code):
            target_versions = [get_version_label(code)]
        else:
            target_versions = build_version_dict(data.lines, base)
        anchors = [section_map[(base, v)] for v in target_versions if (base, v) in section_map]
        status = "mapped" if anchors else "unmapped"
        notes = [] if anchors else [f"No section was found for {base}."]
        entries.append(
            CFEntry(
                row_idx=int(row.get("__source_row", 0) or 0),
                code=code,
                item_name=clean_text(row.get("Item Name")),
                family_name=clean_text(row.get("Family Name")),
                target_versions=target_versions,
                status=status,
                anchors=anchors,
                notes=notes,
            )
        )
    return entries, sections
