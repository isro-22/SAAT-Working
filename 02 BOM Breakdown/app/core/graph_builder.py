from __future__ import annotations

from collections import deque

from .bom_print import with_version_label
from .models import GraphData, WorkbookData
from .vba_compat import clean_text, normalize_component_key


def build_graph(
    data: WorkbookData,
    base_bom: str,
    version_label: str,
    type_filter: list[str] | None = None,
    depth_limit: int = 1,
    search: str = "",
) -> GraphData:
    tagged = with_version_label(data.lines)
    available_boms = set(tagged["__base_bom"].map(clean_text))
    root = clean_text(base_bom)
    search_norm = clean_text(search).casefold()
    type_set = {clean_text(value) for value in type_filter or [] if clean_text(value)}

    nodes_by_id = {
        root: {
            "id": root,
            "label": root,
            "kind": "bom",
            "description": "",
            "depth": 0,
            "match": not search_norm or search_norm in root.casefold(),
        }
    }
    edges = []
    queue = deque([(root, 0)])
    expanded: set[tuple[str, int]] = set()

    while queue:
        parent, depth = queue.popleft()
        if (parent, depth) in expanded or depth >= max(1, depth_limit):
            continue
        expanded.add((parent, depth))
        subset = tagged[tagged["__base_bom"].eq(parent) & tagged["__version_label"].eq(version_label)].copy()
        if subset.empty and version_label != "V1":
            subset = tagged[tagged["__base_bom"].eq(parent) & tagged["__version_label"].eq("V1")].copy()
        if type_set:
            subset = subset[subset["Type"].map(clean_text).isin(type_set)]

        for _, row in subset.iterrows():
            component_no = clean_text(row.get("No."))
            kind = clean_text(row.get("Type"))
            comp_id = component_no if component_no in available_boms else normalize_component_key(row.get("Type"), row.get("No."))
            label = component_no or comp_id
            description = clean_text(row.get("Description"))
            match = not search_norm or search_norm in label.casefold() or search_norm in description.casefold()
            if comp_id not in nodes_by_id:
                nodes_by_id[comp_id] = {
                    "id": comp_id,
                    "label": label,
                    "kind": "bom" if component_no in available_boms else kind,
                    "description": description,
                    "uom": clean_text(row.get("Unit of Measure Code")),
                    "depth": depth + 1,
                    "match": match,
                }
            else:
                nodes_by_id[comp_id]["match"] = bool(nodes_by_id[comp_id].get("match")) or match
            edges.append(
                {
                    "source": parent,
                    "target": comp_id,
                    "qty": row.get("Quantity", ""),
                    "uom": clean_text(row.get("Unit of Measure Code")),
                    "line_no": row.get("Line No.", ""),
                    "description": description,
                    "kind": kind,
                    "depth": depth + 1,
                }
            )
            if component_no in available_boms and depth + 1 < depth_limit:
                queue.append((component_no, depth + 1))

    return GraphData(nodes=list(nodes_by_id.values()), edges=edges, version_label=version_label)


def graph_from_delta(base_bom: str, delta, mode: str = "all") -> GraphData:
    nodes_by_id = {
        base_bom: {
            "id": base_bom,
            "label": base_bom,
            "kind": "bom",
            "description": f"{delta.v_old} vs {delta.v_new}",
            "depth": 0,
            "match": True,
            "delta": "root",
        }
    }
    edges = []

    rows = []
    if mode in {"all", "added"}:
        rows.extend(("added", row) for row in delta.added)
    if mode in {"all", "removed"}:
        rows.extend(("removed", row) for row in delta.removed)
    if mode in {"all", "changed"}:
        collapsed = {}
        for row in delta.changed:
            collapsed.setdefault(row["key"], {"key": row["key"], "fields": []})
            collapsed[row["key"]]["fields"].append(row["field"])
            collapsed[row["key"]]["No."] = row["key"].split("|")[-1]
        rows.extend(("changed", row) for row in collapsed.values())

    for status, row in rows:
        node_id = row["key"]
        nodes_by_id[node_id] = {
            "id": node_id,
            "label": clean_text(row.get("No.")) or node_id.split("|")[-1],
            "kind": clean_text(row.get("Type", "component")),
            "description": clean_text(row.get("Description", "")),
            "depth": 1,
            "match": True,
            "delta": status,
        }
        edges.append(
            {
                "source": clean_text(base_bom),
                "target": node_id,
                "qty": row.get("Quantity", ""),
                "uom": clean_text(row.get("Unit of Measure Code")),
                "line_no": row.get("Line No.", ""),
                "delta": status,
            }
        )
    return GraphData(nodes=list(nodes_by_id.values()), edges=edges, version_label=f"{delta.v_old} vs {delta.v_new}")
