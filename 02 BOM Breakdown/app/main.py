from __future__ import annotations

import json
import hashlib
from html import escape
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from core.bom_print import build_sections_print_all_bom, build_version_dict
from core.bom_tree import build_bom_tree
from core.cf_builder import build_sections_from_cf
from core.delta_view import build_delta_view
from core.excel_io import load_excel, quality_summary
from core.family_export import changed_qty_mask, export_family_workbook
from core.family_compare import build_family_matrix
from core.graph_builder import graph_from_delta
from core.vba_compat import clean_text


st.set_page_config(page_title="Production BOM Analyzer", layout="wide")


st.markdown(
    """
    <style>
    :root {
        --bom-bg: #f5f5f7;
        --bom-panel: rgba(255, 255, 255, 0.88);
        --bom-line: rgba(0, 0, 0, 0.08);
        --bom-text: #1d1d1f;
        --bom-muted: #6e6e73;
        --bom-blue: #0071e3;
        --bom-yellow: #fff3b0;
    }
    .stApp {
        background: radial-gradient(circle at top left, #ffffff 0, #f5f5f7 36%, #ececf1 100%);
        color: var(--bom-text);
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1480px;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    div[data-testid="stMetric"] {
        background: var(--bom-panel);
        border: 1px solid var(--bom-line);
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 14px 38px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetricLabel"] p {
        color: var(--bom-muted);
        font-size: 0.86rem;
    }
    div[data-testid="stMetricValue"] {
        color: var(--bom-text);
        font-size: 1.9rem;
    }
    .bom-hero {
        padding: 28px 0 14px;
    }
    .bom-eyebrow {
        color: var(--bom-blue);
        font-weight: 650;
        font-size: 0.86rem;
    }
    .bom-title {
        font-size: 2.7rem;
        line-height: 1.04;
        font-weight: 760;
        margin: 4px 0 8px;
    }
    .bom-subtitle {
        color: var(--bom-muted);
        font-size: 1.05rem;
        max-width: 880px;
    }
    .bom-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        border: 1px solid var(--bom-line);
        border-radius: 999px;
        background: rgba(255,255,255,0.7);
        color: var(--bom-muted);
        font-size: 0.85rem;
        margin-right: 6px;
    }
    .bom-link-table a {
        color: var(--bom-blue);
        text-decoration: none;
        font-weight: 650;
    }
    .bom-link-table table {
        width: 100%;
    }
    .bom-link-table th, .bom-link-table td {
        padding: 9px 10px;
        border-bottom: 1px solid var(--bom-line);
        text-align: left;
    }
    .tree-node {
        min-height: 58px;
        padding: 8px 12px;
        border: 1px solid rgba(0,0,0,0.07);
        border-radius: 12px;
        background: rgba(255,255,255,0.72);
        box-shadow: 0 6px 18px rgba(0,0,0,0.035);
    }
    .tree-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 760;
        color: #1d1d1f;
    }
    .tree-meta {
        color: #6e6e73;
        font-size: 0.82rem;
        margin-top: 3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .tree-level {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 34px;
        padding: 3px 8px;
        border-radius: 999px;
        color: white;
        font-size: 0.76rem;
        font-weight: 760;
    }
    .tree-sub {
        display: inline-flex;
        padding: 3px 8px;
        border-radius: 999px;
        background: #e8f2ff;
        color: #0071e3;
        font-size: 0.74rem;
        font-weight: 700;
    }
    .tree-leaf {
        display: inline-flex;
        padding: 3px 8px;
        border-radius: 999px;
        background: #f2f2f7;
        color: #6e6e73;
        font-size: 0.74rem;
        font-weight: 650;
    }
    .tree-desc {
        padding: 8px 10px;
        color: #424245;
        font-size: 0.92rem;
        line-height: 1.35;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Generating BOM analysis...")
def generate_analysis(file_bytes: bytes):
    data = load_excel(file_bytes)
    entries, cf_sections = build_sections_from_cf(data)
    return {
        "data": data,
        "summary": quality_summary(data),
        "entries": entries,
        "sections": cf_sections,
    }


def workbook_digest(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def render_section(section):
    st.markdown(f'<a id="{section.anchor_id}"></a>', unsafe_allow_html=True)
    st.subheader(f"BOM BREAKDOWN - {section.base_bom} - {section.version_label}")
    cols = st.columns(4)
    cols[0].metric("BOM No.", section.base_bom)
    cols[1].metric("Version", section.version_label)
    cols[2].metric("Version Code", section.version_code or "(blank)")
    cols[3].metric("Rows", len(section.rows))
    st.caption(section.description)
    for note in section.notes:
        st.info(note)
    st.dataframe(section.rows, width="stretch", hide_index=True)
    with st.expander("Lineage"):
        st.json([ref.__dict__ for ref in section.lineage_refs])


def graph_positions(graph, layout: str) -> dict[str, tuple[float, float]]:
    if not graph.nodes:
        return {}
    if layout == "Hierarchical":
        depth_groups: dict[int, list[str]] = {}
        for node in graph.nodes:
            depth_groups.setdefault(int(node.get("depth", 0)), []).append(node["id"])
        positions = {}
        for depth, ids in depth_groups.items():
            count = max(1, len(ids))
            for index, node_id in enumerate(sorted(ids)):
                positions[node_id] = (index - (count - 1) / 2, -depth)
        return positions

    g = nx.DiGraph()
    g.add_nodes_from(node["id"] for node in graph.nodes)
    g.add_edges_from((edge["source"], edge["target"]) for edge in graph.edges)
    raw = nx.spring_layout(g, seed=42, k=0.9, iterations=80)
    return {node_id: (float(pos[0]), float(pos[1])) for node_id, pos in raw.items()}


def graph_figure(graph, layout: str = "Force", selected_node: str = ""):
    positions = graph_positions(graph, layout)
    edge_x = []
    edge_y = []
    delta_color = {"added": "#34c759", "removed": "#ff3b30", "changed": "#ffcc00"}
    for edge in graph.edges:
        source_pos = positions.get(edge["source"], (0, 0))
        target_pos = positions.get(edge["target"], (0, 0))
        edge_x.extend([source_pos[0], target_pos[0], None])
        edge_y.extend([source_pos[1], target_pos[1], None])

    node_x = []
    node_y = []
    labels = []
    hover = []
    colors = []
    sizes = []
    for node in graph.nodes:
        x, y = positions.get(node["id"], (0, 0))
        node_x.append(x)
        node_y.append(y)
        labels.append(node.get("label", node["id"]))
        hover.append(
            f"{node.get('label', node['id'])}<br>"
            f"Type: {node.get('kind', '')}<br>"
            f"Description: {node.get('description', '')}<br>"
            f"Depth: {node.get('depth', 0)}<br>"
            f"Delta: {node.get('delta', '-')}"
        )
        if selected_node and node["id"] == selected_node:
            colors.append("#0071e3")
            sizes.append(26)
        elif node.get("delta") in delta_color:
            colors.append(delta_color[node["delta"]])
            sizes.append(21)
        elif node.get("kind") == "bom":
            colors.append("#1d1d1f")
            sizes.append(20)
        elif node.get("match"):
            colors.append("#0071e3")
            sizes.append(18)
        else:
            colors.append("#a1a1a6")
            sizes.append(14)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=1.4, color="rgba(110,110,115,0.55)"),
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            hovertext=hover,
            hoverinfo="text",
            marker=dict(size=sizes, color=colors, line=dict(width=1, color="white")),
        )
    )
    fig.update_layout(
        height=620,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.45)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        dragmode="pan",
    )
    return fig


def highlight_changes(frame: pd.DataFrame):
    mask = changed_qty_mask(frame)
    return frame.style.apply(lambda _: mask.map(lambda changed: "background-color: #fff3b0" if changed else ""), axis=None)


@st.cache_data(show_spinner=False)
def cached_family_workbook(file_bytes: bytes, include_all_versions: bool = True) -> bytes:
    return export_family_workbook(file_bytes, include_all_versions=include_all_versions)


def render_dashboard(summary: dict[str, int]):
    st.markdown(
        """
        <div class="bom-hero">
          <div class="bom-eyebrow">Production BOM Intelligence</div>
          <div class="bom-title">Clean lineage, fast comparison, calmer decisions.</div>
          <div class="bom-subtitle">
            This dashboard reads the BOM workbook, validates its structure, prepares versioned sections,
            and opens the workflow for comparison, delta analysis, and BOM tree exploration.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<span class="bom-pill">Dynamic header detection</span><span class="bom-pill">Lineage ready</span>', unsafe_allow_html=True)
    top = st.columns(4)
    top[0].metric("CF Items", f"{summary['cf_items']:,}")
    top[1].metric("BOM Headers", f"{summary['bom_headers']:,}")
    top[2].metric("BOM Lines", f"{summary['bom_lines']:,}")
    top[3].metric("Unique Line BOMs", f"{summary['unique_line_boms']:,}")
    bottom = st.columns(4)
    bottom[0].metric("Header Duplicates", f"{summary['header_duplicates']:,}")
    bottom[1].metric("Qty <= 0", f"{summary['quantity_zero_or_negative']:,}")
    bottom[2].metric("Blank UoM", f"{summary['blank_line_uom']:,}")
    bottom[3].metric("Blank Description", f"{summary['blank_line_description']:,}")


def cf_link_table(cf_table: pd.DataFrame) -> str:
    rows = []
    for _, row in cf_table.iterrows():
        anchors = row.get("anchors") or []
        code = clean_text(row.get("code", ""))
        link = f'<a href="?view=cf_detail&cf={quote(code)}" target="_blank" rel="noopener">Open Detail</a>' if anchors else "-"
        rows.append(
            "<tr>"
            f"<td>{escape(code)}</td>"
            f"<td>{escape(clean_text(row.get('item_name', '')))}</td>"
            f"<td>{escape(clean_text(row.get('family_name', '')))}</td>"
            f"<td>{escape(', '.join(row.get('target_versions', [])))}</td>"
            f"<td>{escape(clean_text(row.get('status', '')))}</td>"
            f"<td>{link}</td>"
            "</tr>"
        )
    return (
        '<div class="bom-link-table"><table>'
        "<thead><tr><th>Item Code</th><th>Item Name</th><th>Family</th><th>Versions</th><th>Status</th><th>Detail</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def cf_detail_url(code: str) -> str:
    return f"?view=cf_detail&cf={quote(clean_text(code))}"


def render_cf_detail_page(entries, all_sections):
    cf_code = clean_text(st.query_params.get("cf", ""))
    entry = next((item for item in entries if item.code == cf_code), None)
    if entry is None:
        st.error("CF item was not found.")
        st.stop()
    sections = [section for section in all_sections if section.anchor_id in entry.anchors]
    st.markdown(
        f"""
        <div class="bom-hero">
          <div class="bom-eyebrow">CF Detail</div>
          <div class="bom-title">{escape(entry.code)}</div>
          <div class="bom-subtitle">{escape(entry.item_name)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        " ".join(
            [
                f'<span class="bom-pill">Family {escape(entry.family_name or "-")}</span>',
                f'<span class="bom-pill">Versions {escape(", ".join(entry.target_versions))}</span>',
                f'<span class="bom-pill">{len(sections)} section</span>',
            ]
        ),
        unsafe_allow_html=True,
    )
    if not sections:
        st.warning("No matching BOM section was found for this CF item.")
    for section in sections:
        render_section(section)


def tree_state_key(base: str, version: str) -> str:
    return f"tree_expanded::{clean_text(base)}::{clean_text(version)}"


def tree_path_key(row: pd.Series) -> str:
    return clean_text(row.get("Path", ""))


def tree_ancestor_keys(path: str) -> list[str]:
    parts = [clean_text(part) for part in path.split(">") if clean_text(part)]
    return [" > ".join(parts[: index + 1]) for index in range(1, max(1, len(parts) - 1))]


def tree_visible_rows(tree: pd.DataFrame, expanded: set[str]) -> pd.DataFrame:
    if tree.empty:
        return tree
    visible_mask = []
    for _, row in tree.iterrows():
        level = int(row.get("Level", 1))
        if level <= 1:
            visible_mask.append(True)
            continue
        visible_mask.append(all(key in expanded for key in tree_ancestor_keys(tree_path_key(row))))
    return tree.loc[visible_mask].copy()


def tree_level_color(level: int) -> str:
    colors = ["#0071e3", "#34c759", "#ff9500", "#af52de", "#ff3b30", "#5ac8fa", "#5856d6", "#6e6e73"]
    return colors[(max(1, level) - 1) % len(colors)]


def render_bom_tree_outline(tree: pd.DataFrame, base: str, version: str):
    key = tree_state_key(base, version)
    expanded = set(st.session_state.get(key, []))
    sub_bom_paths = set(tree.loc[tree["Is Sub-BOM"].fillna(False), "Path"].map(clean_text)) if not tree.empty else set()

    controls = st.columns([1, 1, 4])
    if controls[0].button("Expand All", key=f"{key}::expand_all"):
        st.session_state[key] = sorted(sub_bom_paths)
        st.rerun()
    if controls[1].button("Collapse All", key=f"{key}::collapse_all"):
        st.session_state[key] = []
        st.rerun()
    controls[2].caption("Click ▸ to expand a sub-BOM, or ▾ to collapse it.")

    visible = tree_visible_rows(tree, expanded)
    header = st.columns([0.75, 4.2, 0.8, 0.8, 3.5])
    header[0].markdown("**Level**")
    header[1].markdown("**Component**")
    header[2].markdown("**Qty**")
    header[3].markdown("**UoM**")
    header[4].markdown("**Description**")

    max_rows = 450
    for idx, row in visible.head(max_rows).iterrows():
        level = int(row.get("Level", 1))
        path = tree_path_key(row)
        is_sub_bom = bool(row.get("Is Sub-BOM"))
        is_open = path in expanded
        cols = st.columns([0.75, 4.2, 0.8, 0.8, 3.5])
        if is_sub_bom:
            label = f"L{level} {'▾' if is_open else '▸'}"
            if cols[0].button(label, key=f"{key}::toggle::{idx}::{path}"):
                if is_open:
                    expanded.discard(path)
                    for child_path in list(expanded):
                        if child_path.startswith(f"{path} > "):
                            expanded.discard(child_path)
                else:
                    expanded.add(path)
                st.session_state[key] = sorted(expanded)
                st.rerun()
        else:
            cols[0].markdown(
                f"<span class='tree-level' style='background:{tree_level_color(level)}'>L{level}</span>",
                unsafe_allow_html=True,
            )
        indent_px = max(0, level - 1) * 18
        component = escape(clean_text(row.get("Component No.", "")))
        parent = escape(clean_text(row.get("Parent BOM", "")))
        seq = escape(clean_text(row.get("Seq", "")))
        tag = "<span class='tree-sub'>Sub-BOM</span>" if is_sub_bom else "<span class='tree-leaf'>Leaf</span>"
        cols[1].markdown(
            f"<div class='tree-node' style='margin-left:{indent_px}px;border-left:5px solid {tree_level_color(level)}'>"
            f"<div class='tree-title'><span class='tree-level' style='background:{tree_level_color(level)}'>L{level}</span>"
            f"<span>{component}</span>{tag}</div>"
            f"<div class='tree-meta'>Parent: {parent} · No: {seq}</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        cols[2].write(row.get("Quantity", ""))
        cols[3].write(row.get("UoM", ""))
        cols[4].markdown(f"<div class='tree-desc'>{escape(clean_text(row.get('Description', '')))}</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if len(visible) > max_rows:
        st.caption(f"Showing {max_rows} of {len(visible):,} visible rows. Use Max Level, Collapse, or Search to narrow the tree.")


st.title("Production BOM Analyzer")
uploaded = st.file_uploader("Upload Export BOM.xlsx", type=["xlsx"])
default_workbook = Path("Export BOM.xlsx")
if uploaded is None and default_workbook.exists():
    st.caption("Using local workbook: Export BOM.xlsx")
    workbook_bytes = default_workbook.read_bytes()
elif uploaded is not None:
    workbook_bytes = uploaded.getvalue()
else:
    st.info("Upload a workbook with Production BOM Header, Production BOM Line, and CF List sheets.")
    st.stop()

current_hash = workbook_digest(workbook_bytes)
analysis = st.session_state.get("analysis")
analysis_ready = bool(analysis and analysis.get("file_hash") == current_hash)
is_detail_request = clean_text(st.query_params.get("view", "")) == "cf_detail"

if not analysis_ready:
    if is_detail_request:
        generated = generate_analysis(workbook_bytes)
        generated["file_hash"] = current_hash
        st.session_state["analysis"] = generated
        st.rerun()
    st.markdown(
        """
        <div class="bom-hero">
          <div class="bom-eyebrow">Generation Required</div>
          <div class="bom-title">Generate once. Explore many times.</div>
          <div class="bom-subtitle">
            The workbook has not been processed in this session. Click Generate Analysis to build
            the parser cache, PRINT_ALL_BOM sections, CF mapping, and quality summary. After that,
            each tab only reads the generated view data.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Generate Analysis", type="primary"):
        generated = generate_analysis(workbook_bytes)
        generated["file_hash"] = current_hash
        st.session_state["analysis"] = generated
        st.rerun()
    st.stop()

data = analysis["data"]
summary = analysis["summary"]
entries = analysis["entries"]
all_sections = analysis["sections"]

if clean_text(st.query_params.get("view", "")) == "cf_detail":
    render_cf_detail_page(entries, all_sections)
    st.stop()

tabs = st.tabs(["Overview", "PRINT_ALL_BOM", "CF Explorer", "Family Comparison", "BOM Tree", "Delta View", "Utilities"])

with tabs[0]:
    render_dashboard(summary)
    if data.warnings:
        for warning in data.warnings:
            st.warning(warning)
    st.subheader("Preview")
    for name, frame in [("CF List", data.cf), ("Production BOM Header", data.headers), ("Production BOM Line", data.lines)]:
        with st.expander(name, expanded=name == "CF List"):
            st.caption(f"Header row: {data.header_rows[name]}")
            st.dataframe(frame.head(50), width="stretch", hide_index=True)

with tabs[1]:
    st.header("PRINT_ALL_BOM")
    all_boms = sorted(data.headers["No."].map(clean_text).dropna().unique())
    selected = st.multiselect("Base BOM", all_boms, default=all_boms[:3])
    selected_set = set(selected)
    sections = [section for section in all_sections if section.base_bom in selected_set]
    for section in sections:
        render_section(section)

with tabs[2]:
    st.header("CF Explorer")
    cf_table = pd.DataFrame([e.__dict__ for e in entries])
    search_cf = st.text_input("Search CF item / family", key="cf_search")
    filtered_entries = [
        entry
        for entry in entries
        if not search_cf
        or search_cf.casefold() in entry.code.casefold()
        or search_cf.casefold() in entry.item_name.casefold()
        or search_cf.casefold() in entry.family_name.casefold()
    ]
    st.caption("Click Open Detail to open the BOM detail page in a new tab.")
    header_cols = st.columns([1.5, 2.8, 1.6, 1.2, 1.0])
    header_cols[0].markdown("**Item Code**")
    header_cols[1].markdown("**Item Name**")
    header_cols[2].markdown("**Family**")
    header_cols[3].markdown("**Versions**")
    header_cols[4].markdown("**Action**")
    for entry in filtered_entries[:80]:
        row_cols = st.columns([1.5, 2.8, 1.6, 1.2, 1.0])
        row_cols[0].write(entry.code)
        row_cols[1].write(entry.item_name)
        row_cols[2].write(entry.family_name)
        row_cols[3].write(", ".join(entry.target_versions))
        row_cols[4].markdown(
            f'<a href="{cf_detail_url(entry.code)}" target="_blank" rel="noopener">Open Detail</a>',
            unsafe_allow_html=True,
        )
    if len(filtered_entries) > 80:
        st.caption(f"Showing 80 of {len(filtered_entries)} results. Use search to narrow the list.")
    with st.expander("Raw CF Link Table"):
        st.markdown(cf_link_table(pd.DataFrame([e.__dict__ for e in filtered_entries[:120]])), unsafe_allow_html=True)
    failed = cf_table[cf_table["status"].eq("unmapped")] if not cf_table.empty else cf_table
    if not failed.empty:
        st.warning(f"{len(failed)} CF items could not be mapped.")

with tabs[3]:
    st.header("Family Comparison")
    families = sorted(x for x in data.cf["Family Name"].map(clean_text).unique() if x)
    family = st.selectbox("Family Name", families)
    include_all = st.toggle("Include All Versions", value=True)
    matrix = build_family_matrix(data, family, include_all_versions=include_all)
    if matrix.empty:
        st.info("No data is available for this family.")
    else:
        st.dataframe(highlight_changes(matrix), width="stretch", hide_index=True)
        st.caption("Yellow cells mark Quantity differences across items or versions for the same component row.")
        c1, c2 = st.columns(2)
        c1.download_button("Download Current Family CSV", matrix.to_csv(index=False).encode("utf-8"), f"{family}_comparison.csv", "text/csv")
        xlsx_bytes = cached_family_workbook(workbook_bytes, include_all_versions=include_all)
        c2.download_button(
            "Download All Families XLSX",
            xlsx_bytes,
            "all_family_comparison.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

with tabs[4]:
    st.header("BOM Tree")
    base_options = sorted(data.lines["Production BOM No."].map(clean_text).unique())
    base = st.selectbox("Base BOM", base_options, index=0, key="tree_base")
    versions = build_version_dict(data.lines, base)
    control_cols = st.columns([1.0, 1.0, 1.4])
    version = control_cols[0].selectbox("Version", versions, key="tree_version")
    depth = control_cols[1].slider("Max Level", min_value=1, max_value=8, value=4)
    search_node = control_cols[2].text_input("Search component / description / path", key="tree_search")
    available_types = sorted(x for x in data.lines["Type"].map(clean_text).unique() if x)
    type_filter = st.multiselect("Filter Type", available_types, default=[], key="tree_type_filter")
    tree = build_bom_tree(data, base, version_label=version, max_depth=depth, type_filter=type_filter)
    level_counts = tree.groupby("Level").size().reset_index(name="Rows") if not tree.empty else pd.DataFrame(columns=["Level", "Rows"])
    c_tree_1, c_tree_2, c_tree_3, c_tree_4 = st.columns(4)
    c_tree_1.metric("Rows", f"{len(tree):,}")
    c_tree_2.metric("Max Level", int(tree["Level"].max()) if not tree.empty else 0)
    c_tree_3.metric("Sub-BOM Nodes", int(tree["Is Sub-BOM"].sum()) if not tree.empty else 0)
    c_tree_4.metric("Version", version)

    if tree.empty:
        st.info("No BOM tree structure is available for the current filter.")
    else:
        if search_node:
            needle = search_node.casefold()
            searchable = tree[["Tree", "Component No.", "Description", "Path"]].astype(str).agg(" ".join, axis=1).str.casefold()
            search_result = tree[searchable.str.contains(needle, regex=False)].copy()
            st.caption("Search is active: results are shown as a compact list so paths are easier to read.")
            st.dataframe(search_result[["Level", "Tree", "Quantity", "UoM", "Description", "Path"]], width="stretch", hide_index=True)
            export_view = search_result
        else:
            render_bom_tree_outline(tree, base, version)
            export_view = tree

        with st.expander("Table & Export"):
            st.dataframe(
                export_view,
                width="stretch",
                hide_index=True,
                column_config={
                    "Level": st.column_config.NumberColumn("Level", width="small"),
                    "Tree": st.column_config.TextColumn("BOM Tree", width="large"),
                    "Cumulative Qty": st.column_config.NumberColumn("Cumulative Qty", format="%.6f"),
                    "Is Sub-BOM": st.column_config.CheckboxColumn("Sub-BOM"),
                    "Path": st.column_config.TextColumn("Path", width="large"),
                },
            )
            c_export_1, c_export_2 = st.columns(2)
            c_export_1.download_button(
                "Download Tree CSV",
                export_view.to_csv(index=False).encode("utf-8"),
                f"{base}_{version}_bom_tree.csv",
                "text/csv",
            )
            c_export_2.download_button(
                "Download Tree JSON",
                json.dumps(export_view.to_dict(orient="records"), default=str, indent=2),
                f"{base}_{version}_bom_tree.json",
                "application/json",
            )
    with st.expander("Level Summary"):
        st.dataframe(level_counts, width="stretch", hide_index=True)

with tabs[5]:
    st.header("Delta View")
    base_options = sorted(data.lines["Production BOM No."].map(clean_text).unique())
    base = st.selectbox("Base BOM", base_options, index=0, key="delta_base")
    versions = build_version_dict(data.lines, base)
    c1, c2 = st.columns(2)
    v_old = c1.selectbox("Old Version", versions, index=0)
    v_new = c2.selectbox("New Version", versions, index=min(1, len(versions) - 1))
    delta = build_delta_view(data.lines, base, v_old, v_new)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Added", len(delta.added))
    metric_cols[1].metric("Removed", len(delta.removed))
    metric_cols[2].metric("Changed Fields", len(delta.changed))
    metric_cols[3].metric("Versions", f"{v_old} -> {v_new}")
    delta_filter = st.segmented_control("Show", ["Summary", "Added", "Removed", "Changed", "Graph"], default="Summary")

    added_df = pd.DataFrame(delta.added)
    removed_df = pd.DataFrame(delta.removed)
    changed_df = pd.DataFrame(delta.changed)
    if delta_filter == "Summary":
        summary_rows = [
            {"Status": "Added", "Count": len(delta.added)},
            {"Status": "Removed", "Count": len(delta.removed)},
            {"Status": "Changed Fields", "Count": len(delta.changed)},
        ]
        st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)
        st.caption("Choose Added, Removed, or Changed for details, or Graph for a visual delta.")
    elif delta_filter == "Added":
        st.dataframe(added_df, width="stretch", hide_index=True)
    elif delta_filter == "Removed":
        st.dataframe(removed_df, width="stretch", hide_index=True)
    elif delta_filter == "Changed":
        if changed_df.empty:
            st.info("No fields changed.")
        else:
            st.dataframe(
                changed_df.style.map(lambda _: "background-color: #fff3b0", subset=["from", "to"]),
                width="stretch",
                hide_index=True,
            )
    else:
        mode = st.segmented_control("Delta Graph Layer", ["all", "added", "removed", "changed"], default="all", key="delta_graph_mode")
        delta_graph = graph_from_delta(base, delta, mode=mode)
        st.plotly_chart(graph_figure(delta_graph, layout="Hierarchical"), width="stretch")
        st.dataframe(pd.DataFrame(delta_graph.edges), width="stretch", hide_index=True)

    export_delta = {
        "base_bom": base,
        "old": v_old,
        "new": v_new,
        "added": delta.added,
        "removed": delta.removed,
        "changed": delta.changed,
    }
    st.download_button("Export Delta JSON", json.dumps(export_delta, default=str, indent=2), f"{base}_{v_old}_vs_{v_new}_delta.json")

with tabs[6]:
    st.header("Utilities")
    if st.button("Clear Generated Analysis / Reset Cache"):
        st.session_state.pop("analysis", None)
        st.cache_data.clear()
        st.success("Generated analysis and Streamlit cache were cleared.")
        st.rerun()
