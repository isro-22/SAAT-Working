from __future__ import annotations

from html import escape
from urllib.parse import quote

import streamlit as st

from .data_engine import (
    SEARCH_FIELD_GROUPS,
    analytics_summary,
    clean_value,
    descriptor_terms,
    detail_sections,
    format_organoleptic_text,
    format_synonyms,
    first_available,
    get_material,
    material_id,
    search_materials,
    similar_materials,
    summarize_material,
    truncate,
)


st.set_page_config(
    page_title="Flavor Chemical Database",
    page_icon="FC",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --black: #000000;
            --yellow: #FFE500;
            --pink: #FF5C8A;
            --cyan: #61D7FF;
            --green: #71F79F;
            --paper: #FFFDF2;
        }

        html, body, [class*="css"] {
            font-family: Arial, Helvetica, sans-serif;
        }

        .stApp {
            background:
                linear-gradient(90deg, rgba(0,0,0,.05) 1px, transparent 1px),
                linear-gradient(rgba(0,0,0,.05) 1px, transparent 1px),
                var(--paper);
            background-size: 26px 26px;
            color: var(--black);
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 4rem;
            max-width: 1280px;
        }

        .auto-nav {
            position: sticky;
            top: 0;
            z-index: 9999;
            width: max-content;
            max-width: 100%;
            height: 34px;
            overflow: hidden;
            border: 5px solid var(--black);
            box-shadow: 7px 7px 0 var(--black);
            background: var(--yellow);
            margin: 0 auto 16px;
            transition: height .16s ease, background .16s ease;
        }

        .auto-nav:hover,
        .auto-nav:focus-within {
            height: 84px;
            background: white;
        }

        .nav-handle {
            height: 28px;
            display: grid;
            place-items: center;
            color: var(--black);
            font-size: .78rem;
            font-weight: 900;
            letter-spacing: 0;
        }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px 12px;
        }

        .nav-link {
            display: inline-block;
            border: 4px solid var(--black);
            background: white;
            color: var(--black) !important;
            padding: 8px 14px;
            font-weight: 900;
            text-decoration: none !important;
            text-transform: uppercase;
            min-width: 105px;
            text-align: center;
        }

        .nav-link.active {
            background: var(--yellow);
        }

        .hero {
            border: 6px solid var(--black);
            box-shadow: 10px 10px 0 var(--black);
            background: var(--yellow);
            padding: 28px 30px;
            margin-bottom: 28px;
        }

        .hero h1 {
            color: var(--black);
            font-size: clamp(2.2rem, 6vw, 5.8rem);
            line-height: .9;
            margin: 0;
            font-weight: 900;
            letter-spacing: 0;
        }

        .hero p {
            max-width: 900px;
            color: var(--black);
            font-size: 1rem;
            margin: 18px 0 0;
            font-weight: 800;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stMultiSelect"] div,
        div[data-testid="stSelectbox"] div {
            border-radius: 0;
        }

        div[data-testid="stTextInput"] input {
            border: 5px solid var(--black);
            box-shadow: 7px 7px 0 var(--black);
            min-height: 58px;
            font-weight: 900;
            font-size: 1rem;
            background: white;
        }

        div[data-testid="stMultiSelect"] > div > div {
            border: 5px solid var(--black);
            box-shadow: 7px 7px 0 var(--black);
            background: white;
            min-height: 58px;
            font-weight: 900;
        }

        .stButton > button {
            border: 5px solid var(--black);
            border-radius: 0;
            box-shadow: 7px 7px 0 var(--black);
            background: white;
            color: var(--black);
            font-weight: 900;
            min-height: 48px;
            transition: transform .08s ease, box-shadow .08s ease;
        }

        .stButton > button:hover,
        .stButton > button:focus {
            border-color: var(--black);
            color: var(--black);
            background: var(--yellow);
            transform: translate(3px, 3px);
            box-shadow: 4px 4px 0 var(--black);
        }

        .field-filter-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            margin: 4px 0 18px;
            border: 5px solid var(--black);
            box-shadow: 7px 7px 0 var(--black);
            background: white;
            padding: 10px;
        }

        .field-filter {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: 3px solid var(--black);
            background: white;
            color: var(--black) !important;
            padding: 7px 9px;
            font-size: .74rem;
            font-weight: 900;
            text-decoration: none !important;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .field-filter.active {
            background: var(--yellow);
        }

        .filter-mark {
            display: inline-grid;
            place-items: center;
            width: 16px;
            height: 16px;
            border: 3px solid var(--black);
            background: white;
            line-height: 1;
            font-size: .68rem;
        }

        .field-filter.active .filter-mark {
            background: var(--black);
            color: white;
        }

        div[data-testid="stForm"] {
            border: 5px solid var(--black);
            box-shadow: 7px 7px 0 var(--black);
            background: white;
            padding: 10px 12px 2px;
            margin: 4px 0 18px;
        }

        div[data-testid="stForm"] label {
            font-weight: 900;
            font-size: .78rem;
            white-space: nowrap;
        }

        .card {
            border: 5px solid var(--black);
            box-shadow: 8px 8px 0 var(--black);
            background: white;
            padding: 18px;
            min-height: 245px;
            margin-bottom: 20px;
        }

        .card h3 {
            color: var(--black);
            font-size: 1.18rem;
            line-height: 1.15;
            margin: 0 0 12px;
            font-weight: 900;
            letter-spacing: 0;
        }

        .tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }

        .tag {
            border: 3px solid var(--black);
            background: var(--cyan);
            color: var(--black);
            padding: 4px 8px;
            font-size: .76rem;
            font-weight: 900;
        }

        .tag:nth-child(2) {
            background: var(--green);
        }

        .card p {
            color: var(--black);
            font-size: .9rem;
            font-weight: 800;
            margin: 0;
        }

        .results-panel {
            border: 6px solid var(--black);
            box-shadow: 10px 10px 0 var(--black);
            background: white;
            padding: 18px;
            margin-top: 18px;
            overflow-x: auto;
        }

        .results-summary {
            border: 5px solid var(--black);
            background: var(--yellow);
            box-shadow: 7px 7px 0 var(--black);
            padding: 12px 14px;
            margin: 16px 0 18px;
            font-weight: 900;
            color: var(--black);
        }

        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin: 18px 0;
        }

        .analytics-card {
            border: 5px solid var(--black);
            box-shadow: 7px 7px 0 var(--black);
            background: white;
            padding: 18px;
            min-height: 118px;
        }

        .analytics-card span {
            display: block;
            font-size: .78rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .analytics-card strong {
            display: block;
            margin-top: 8px;
            font-size: 2rem;
            line-height: 1;
        }

        .analytics-card:nth-child(2n) {
            background: var(--yellow);
        }

        .compact-table {
            width: 100%;
            border-collapse: collapse;
            color: var(--black);
        }

        .compact-table th,
        .compact-table td {
            border: 3px solid var(--black);
            padding: 10px;
            font-weight: 900;
            text-align: left;
            vertical-align: top;
        }

        .compact-table th {
            background: var(--yellow);
            text-transform: uppercase;
            font-size: .78rem;
        }

        .results-table {
            width: 100%;
            min-width: 980px;
            border-collapse: collapse;
            color: var(--black);
        }

        .results-table th {
            text-align: left;
            font-size: .82rem;
            font-weight: 900;
            text-transform: uppercase;
            padding: 16px 12px;
            border-bottom: 5px solid var(--black);
            background: var(--yellow);
        }

        .results-table td {
            padding: 16px 12px;
            border-bottom: 3px solid var(--black);
            font-size: .9rem;
            font-weight: 800;
            vertical-align: top;
        }

        .results-table tr:nth-child(odd) td {
            background: #F1ECE8;
        }

        .results-table tr:nth-child(even) td {
            background: #FFFFFF;
        }

        .material-link {
            color: var(--black) !important;
            font-weight: 900;
            text-decoration: underline;
            text-decoration-thickness: 3px;
            text-underline-offset: 4px;
        }

        .name-detail {
            max-width: 430px;
            overflow-wrap: anywhere;
        }

        .panel {
            border: 6px solid var(--black);
            box-shadow: 10px 10px 0 var(--black);
            background: white;
            padding: 24px;
            margin-top: 18px;
        }

        .metric-strip {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin: 18px 0;
        }

        .metric-box {
            border: 4px solid var(--black);
            background: var(--yellow);
            padding: 12px;
        }

        .metric-box span {
            display: block;
            font-size: .72rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .metric-box strong {
            display: block;
            font-size: 1rem;
            overflow-wrap: anywhere;
        }

        div[role="radiogroup"] {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        div[role="radiogroup"] label {
            border: 5px solid var(--black);
            box-shadow: 6px 6px 0 var(--black);
            background: white;
            padding: 10px 16px;
            min-width: 145px;
            justify-content: center;
        }

        div[role="radiogroup"] label:has(input:checked) {
            background: var(--yellow);
        }

        div[role="radiogroup"] p {
            font-weight: 900;
            color: var(--black);
        }

        .field-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 14px;
        }

        .field {
            border: 4px solid var(--black);
            background: #ffffff;
            padding: 14px;
            min-height: 98px;
        }

        .field span {
            display: block;
            font-size: .74rem;
            font-weight: 900;
            text-transform: uppercase;
            margin-bottom: 8px;
            color: var(--black);
        }

        .field strong {
            display: block;
            font-size: .96rem;
            line-height: 1.35;
            overflow-wrap: anywhere;
            color: var(--black);
        }

        .detail-list {
            border: 5px solid var(--black);
            background: white;
        }

        .detail-row {
            display: grid;
            grid-template-columns: minmax(180px, 30%) 1fr;
            border-bottom: 3px solid var(--black);
        }

        .detail-row:last-child {
            border-bottom: 0;
        }

        .detail-row:nth-child(odd) {
            background: #F1ECE8;
        }

        .detail-row:nth-child(even) {
            background: white;
        }

        .detail-label,
        .detail-value {
            padding: 16px 18px;
            color: var(--black);
            font-weight: 900;
            line-height: 1.45;
            overflow-wrap: anywhere;
        }

        .detail-label {
            border-right: 3px solid var(--black);
            text-transform: uppercase;
            font-size: .82rem;
        }

        .detail-value {
            font-size: .94rem;
            white-space: pre-line;
        }

        .descriptor-group {
            margin-bottom: 10px;
        }

        .descriptor-title {
            display: block;
            margin-bottom: 8px;
            font-size: .8rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .descriptor-chip {
            display: inline-block;
            border: 3px solid var(--black);
            background: var(--cyan);
            color: var(--black) !important;
            padding: 5px 8px;
            margin: 0 6px 8px 0;
            font-size: .78rem;
            font-weight: 900;
            text-decoration: none !important;
        }

        .descriptor-chip:nth-child(2n) {
            background: var(--green);
        }

        .descriptor-chip:hover {
            background: var(--yellow);
        }

        @media (max-width: 760px) {
            .detail-row {
                grid-template-columns: 1fr;
            }

            .detail-label {
                border-right: 0;
                border-bottom: 2px solid var(--black);
                padding-bottom: 8px;
            }

            .detail-value {
                padding-top: 10px;
            }
        }

        .no-results {
            border: 6px solid var(--black);
            box-shadow: 8px 8px 0 var(--black);
            background: var(--pink);
            color: var(--black);
            padding: 24px;
            font-weight: 900;
            font-size: 1.2rem;
        }

        h2, h3, label, .stMarkdown {
            color: var(--black);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.html(
        """
        <section class="hero">
            <h1>FLAVOR CHEMICAL DATABASE</h1>
            <p>Search flavor and fragrance materials by identifiers, sensory profile, synonyms, and natural occurrence.</p>
        </section>
        """
    )


def render_nav() -> str:
    current_view = st.query_params.get("view", "search")
    search_class = " active" if current_view not in {"analytics", "shelf", "formulation"} else ""
    analytics_class = " active" if current_view == "analytics" else ""
    st.markdown(
        f"""
        <nav class="auto-nav">
            <div class="nav-handle">MENU</div>
            <div class="nav-links">
                <a class="nav-link{search_class}" href="?">Search</a>
                <a class="nav-link{analytics_class}" href="?view=analytics">Analytics</a>
                <a class="nav-link{' active' if current_view == 'shelf' else ''}" href="?view=shelf">My Shelf</a>
                <a class="nav-link{' active' if current_view == 'formulation' else ''}" href="?view=formulation">Formulation Sheet</a>
            </div>
        </nav>
        """,
        unsafe_allow_html=True,
    )
    return current_view


def render_formulation_placeholder() -> None:
    st.html(
        """
        <section class="hero">
            <h1>FORMULATION SHEET</h1>
            <p>Coming soon. This workspace will support formula drafts, dosage notes, material percentages, and exportable formulation records.</p>
        </section>
        <section class="panel">
            <div class="no-results">Under construction. The formulation workspace is reserved for the next build phase.</div>
        </section>
        """
    )


def render_analytics() -> None:
    summary = analytics_summary()
    total = summary["total"]
    coverage = summary["coverage"]
    descriptor_total = sum(count for _, count in summary["top_descriptors"])

    st.html(
        f"""
        <section class="hero">
            <h1>DATA ANALYTICS</h1>
            <p>Coverage, organoleptic patterns, occurrence sources, and data quality signals.</p>
        </section>
        <div class="analytics-grid">
            <div class="analytics-card"><span>Total Materials</span><strong>{total:,}</strong></div>
            <div class="analytics-card"><span>CAS Coverage</span><strong>{coverage_percent(coverage["CAS"], total)}</strong></div>
            <div class="analytics-card"><span>FEMA Coverage</span><strong>{coverage_percent(coverage["FEMA"], total)}</strong></div>
            <div class="analytics-card"><span>Descriptor Hits</span><strong>{descriptor_total:,}</strong></div>
        </div>
        """,
    )

    st.html(f'<section class="panel"><h2>Identifier Coverage</h2>{coverage_table(coverage, total)}</section>')

    left, right = st.columns(2)
    with left:
        st.html(
            f'<section class="panel"><h2>Top Organoleptic Descriptors</h2>{ranking_table(summary["top_descriptors"], "Descriptor")}</section>'
        )
    with right:
        st.html(
            f'<section class="panel"><h2>Top Occurrences</h2>{ranking_table(summary["top_occurrences"], "Occurrence")}</section>'
        )

    left, right = st.columns(2)
    with left:
        st.html(
            f'<section class="panel"><h2>Duplicate CAS</h2>{dict_table(summary["duplicate_cas"], ["value", "count"])}</section>'
        )
    with right:
        st.html(
            f'<section class="panel"><h2>Duplicate Names</h2>{dict_table(summary["duplicate_names"], ["value", "count"])}</section>'
        )

    left, right = st.columns(2)
    with left:
        st.html(
            f'<section class="panel"><h2>CAS Format Issues</h2>{dict_table(summary["weird_cas"], ["name", "cas", "fema", "issue"])}</section>'
        )
    with right:
        st.html(
            f'<section class="panel"><h2>Missing Core Identifiers</h2>{dict_table(summary["empty_core_identifiers"], ["name", "cas", "fema", "issue"])}</section>'
        )


def coverage_percent(value: int, total: int) -> str:
    return f"{(value / total * 100):.1f}%" if total else "0.0%"


def coverage_table(coverage: dict[str, int], total: int) -> str:
    rows = "".join(
        f"<tr><td>{escape(label)}</td><td>{count:,}</td><td>{coverage_percent(count, total)}</td></tr>"
        for label, count in coverage.items()
    )
    return f'<table class="compact-table"><thead><tr><th>Field</th><th>Filled</th><th>Coverage</th></tr></thead><tbody>{rows}</tbody></table>'


def ranking_table(items: list[tuple[str, int]], label: str) -> str:
    rows = "".join(
        f'<tr><td><a class="material-link" href="?q={quote(value)}&fields=Organoleptic">{escape(value)}</a></td><td>{count:,}</td></tr>'
        for value, count in items
    )
    return f'<table class="compact-table"><thead><tr><th>{escape(label)}</th><th>Count</th></tr></thead><tbody>{rows}</tbody></table>'


def dict_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    if not rows:
        return '<div class="no-results">No issues found.</div>'
    header = "".join(f"<th>{escape(column.replace('_', ' ').title())}</th>" for column in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(row.get(column, 'N/A'))}</td>" for column in columns) + "</tr>"
        for row in rows
    )
    return f'<table class="compact-table"><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>'


def render_shelf() -> None:
    shelf_ids = st.session_state.shelf
    materials = [material for material_id_value in shelf_ids if (material := get_material(material_id_value))]

    st.html(
        """
        <section class="hero">
            <h1>MY SHELF</h1>
            <p>Saved materials for comparison and formulation exploration.</p>
        </section>
        """
    )

    if not materials:
        st.html('<div class="no-results">Your shelf is empty. Open a material detail page and add it to the shelf.</div>')
        if st.button("Go to Search", use_container_width=True):
            st.query_params.clear()
            st.rerun()
        return

    st.html(f'<section class="panel"><h2>Saved Materials</h2>{shelf_table(materials)}</section>')
    render_shelf_actions(materials)
    render_compare(materials)


def shelf_table(materials: list[dict]) -> str:
    rows = "".join(
        f"""
        <tr>
            <td><a class="material-link" href="?material={quote(material_id(item), safe='')}">{escape(clean_value(item.get("name")))}</a></td>
            <td>{escape(clean_value(item.get("cas")))}</td>
            <td>{escape(clean_value(item.get("fema")))}</td>
            <td>{escape(truncate(first_available(item, "odor", "flavor", "organoleptic_notes"), 90))}</td>
        </tr>
        """
        for item in materials
    )
    return f'<table class="compact-table"><thead><tr><th>Material</th><th>CAS</th><th>FEMA</th><th>Profile</th></tr></thead><tbody>{rows}</tbody></table>'


def render_shelf_actions(materials: list[dict]) -> None:
    columns = st.columns(min(4, len(materials)) + 1)
    with columns[0]:
        if st.button("Clear Shelf", use_container_width=True):
            st.session_state.shelf = []
            st.rerun()
    for column, item in zip(columns[1:], materials[:3]):
        with column:
            if st.button(f"Remove {truncate(clean_value(item.get('name')), 18)}", key=f"remove_{material_id(item)}", use_container_width=True):
                st.session_state.shelf = [value for value in st.session_state.shelf if value != material_id(item)]
                st.rerun()


def render_compare(materials: list[dict]) -> None:
    if len(materials) < 2:
        st.html('<div class="results-summary">Add at least two materials to unlock comparison.</div>')
        return

    fields = [
        ("Name", "name"),
        ("CAS", "cas"),
        ("FEMA", "fema"),
        ("EINECS", "einecs"),
        ("JECFA Flavoring", "jecfa_food_flavoring"),
        ("Formula", "molecular_formula"),
        ("Molecular Weight", "molecular_weight"),
        ("Boiling Point", "boiling_point"),
        ("Melting Point", "melting_point"),
        ("Solubility", "soluble_in"),
        ("Odor", "odor"),
        ("Taste / Flavor", "flavor"),
        ("Occurrence", "occurrence"),
    ]
    selected = materials[:4]
    header = "<th>Field</th>" + "".join(f"<th>{escape(clean_value(item.get('name')))}</th>" for item in selected)
    rows = ""
    for label, field in fields:
        rows += "<tr>"
        rows += f"<td>{escape(label)}</td>"
        rows += "".join(f"<td>{escape(truncate(clean_value(item.get(field)), 160))}</td>" for item in selected)
        rows += "</tr>"

    st.html(
        f'<section class="panel"><h2>Compare Materials</h2><table class="compact-table"><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></section>'
    )


def render_field_filters(selected_fields: list[str], query: str) -> list[str]:
    labels = list(SEARCH_FIELD_GROUPS.keys())
    form_key = "field_filter_form_" + "_".join(selected_fields)

    with st.form(form_key):
        columns = st.columns([1.1, 0.9, 1.0, 1.2, 1.4, 0.8, 0.9, 0.9, 1.1])
        selected_from_form: list[str] = []
        for column, label in zip(columns[:-1], labels):
            with column:
                checked = st.checkbox(label, value=label in selected_fields, key=f"{form_key}_{label}")
                if checked:
                    selected_from_form.append(label)

        with columns[-1]:
            submitted = st.form_submit_button("Apply Filters", use_container_width=True)

    if submitted:
        if "All fields" in selected_from_form or not selected_from_form:
            selected_from_form = ["All fields"]
        st.session_state.search_fields = selected_from_form
        st.session_state.page = 1
        set_search_query_params(query, selected_from_form, 1)
        st.rerun()

    return selected_fields


def render_results(results: list[dict], page: int, page_size: int) -> None:
    total_results = len(results)
    total_pages = max(1, (total_results + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    page_results = results[start:end]

    st.html(
        f'<div class="results-summary">{total_results} materials found. Page {page} of {total_pages}. Showing {len(page_results)} per page.</div>'
    )
    if not results:
        st.html('<div class="no-results">No results found. Try another keyword or search all fields.</div>')
        return

    rows = "\n".join(render_result_row(material) for material in page_results)
    st.html(
        f"""
        <section class="results-panel">
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Ingredient</th>
                        <th>Name Detail</th>
                        <th>FEMA</th>
                        <th>CAS</th>
                        <th>EINECS</th>
                        <th>JECFA</th>
                        <th>Shelf</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </section>
        """
    )
    render_pagination(page, total_pages)


def render_pagination(page: int, total_pages: int) -> None:
    if total_pages <= 1:
        return

    labels = pagination_labels(page, total_pages)
    columns = st.columns(len(labels) + 2)
    with columns[0]:
        if st.button("Prev", disabled=page <= 1, use_container_width=True):
            st.session_state.page = page - 1
            st.rerun()

    for index, label in enumerate(labels, start=1):
        disabled = label == "..."
        button_label = f"[{label}]" if label == str(page) else label
        with columns[index]:
            if st.button(button_label, disabled=disabled, key=f"page_{label}_{index}", use_container_width=True):
                st.session_state.page = int(label)
                st.rerun()

    with columns[-1]:
        if st.button("Next", disabled=page >= total_pages, use_container_width=True):
            st.session_state.page = page + 1
            st.rerun()


def pagination_labels(page: int, total_pages: int) -> list[str]:
    if total_pages <= 7:
        return [str(number) for number in range(1, total_pages + 1)]

    candidates = {1, 2, total_pages - 1, total_pages, page - 1, page, page + 1}
    numbers = sorted(number for number in candidates if 1 <= number <= total_pages)
    labels: list[str] = []
    previous = 0
    for number in numbers:
        if previous and number - previous > 1:
            labels.append("...")
        labels.append(str(number))
        previous = number
    return labels


def render_result_row(material: dict) -> str:
    summary = summarize_material(material)
    material_id_value = quote(summary["id"], safe="")
    detail = first_available(material, "description", "synonyms", "organoleptic_notes")
    jecfa = first_available(material, "jecfa_food_flavoring", "jecfa_food_additive")
    return f"""
        <tr>
            <td><a class="material-link" href="?material={material_id_value}">{escape(summary["name"])}</a></td>
            <td class="name-detail">{escape(truncate(detail, 92))}</td>
            <td>{escape(summary["fema"])}</td>
            <td>{escape(summary["cas"])}</td>
            <td>{escape(clean_value(material.get("einecs")))}</td>
            <td>{escape(jecfa)}</td>
            <td><a class="material-link" href="?add_shelf={material_id_value}">+ Shelf</a></td>
        </tr>
    """


def render_detail(material: dict) -> None:
    summary = summarize_material(material)
    sections = detail_sections(material)

    nav_columns = st.columns([1, 1, 4])
    with nav_columns[0]:
        if st.button("Back to search", key="back_to_search", use_container_width=True):
            st.session_state.selected_material = None
            st.query_params.clear()
            st.rerun()
    with nav_columns[1]:
        current_id = material_id(material)
        on_shelf = current_id in st.session_state.shelf
        shelf_label = "Remove Shelf" if on_shelf else "Add Shelf"
        if st.button(shelf_label, key=f"shelf_{current_id}", use_container_width=True):
            if on_shelf:
                st.session_state.shelf = [value for value in st.session_state.shelf if value != current_id]
            else:
                st.session_state.shelf.append(current_id)
            st.rerun()

    st.html(
        f"""
        <div class="panel">
            <h2>{escape(summary["name"])}</h2>
            <div class="metric-strip">
                <div class="metric-box"><span>CAS</span><strong>{escape(summary["cas"])}</strong></div>
                <div class="metric-box"><span>FEMA</span><strong>{escape(summary["fema"])}</strong></div>
                <div class="metric-box"><span>Material ID</span><strong>{escape(summary["id"])}</strong></div>
            </div>
        </div>
        """
    )

    active_tab = st.radio(
        "Detail section",
        list(sections.keys()),
        horizontal=True,
        label_visibility="collapsed",
        key="active_tab",
    )

    fields = sections[active_tab]
    if active_tab == "Identifier":
        render_detail_list(identifier_list_fields(material))
    elif active_tab == "Organoleptic":
        render_detail_list(organoleptic_list_fields(material))
    else:
        field_html = "".join(
            f'<div class="field"><span>{escape(label)}</span><strong>{escape(value)}</strong></div>'
            for label, value in fields.items()
        )
        st.html(f'<section class="panel"><div class="field-grid">{field_html}</div></section>')

    render_similar_materials(material)


def render_similar_materials(material: dict) -> None:
    similar = similar_materials(material, limit=8)
    if not similar:
        return

    rows = "".join(
        f"""
        <tr>
            <td><a class="material-link" href="?material={quote(material_id(row["material"]), safe='')}">{escape(clean_value(row["material"].get("name")))}</a></td>
            <td>{escape(row["score"])}</td>
            <td>{escape(row["shared"])}</td>
            <td>{escape(clean_value(row["material"].get("cas")))}</td>
            <td>{escape(clean_value(row["material"].get("fema")))}</td>
        </tr>
        """
        for row in similar
    )
    st.html(
        f'<section class="panel"><h2>Similar Materials</h2><table class="compact-table"><thead><tr><th>Material</th><th>Score</th><th>Shared Signals</th><th>CAS</th><th>FEMA</th></tr></thead><tbody>{rows}</tbody></table></section>'
    )


def render_detail_list(fields: dict[str, str]) -> None:
    row_html = "".join(
        f'<div class="detail-row"><div class="detail-label">{escape(label)}</div><div class="detail-value">{value}</div></div>'
        for label, value in fields.items()
    )
    st.html(f'<section class="panel"><div class="detail-list">{row_html}</div></section>')


def identifier_list_fields(material: dict) -> dict[str, str]:
    return {
        "CAS": escaped_text(clean_value(material.get("cas"))),
        "FEMA": escaped_text(clean_value(material.get("fema"))),
        "EINECS": escaped_text(clean_value(material.get("einecs"))),
        "Name Detail": escaped_text(first_available(material, "description", "name")),
        "Synonyms": escaped_text(format_synonyms(material.get("synonyms"))),
        "JECFA Food Flavoring": escaped_text(clean_value(material.get("jecfa_food_flavoring"))),
        "JECFA Food Additive": escaped_text(clean_value(material.get("jecfa_food_additive"))),
        "DG SANTE Food Flavourings": escaped_text(clean_value(material.get("dg_sante_food_flavourings"))),
        "DG SANTE Food Contact Materials": escaped_text(clean_value(material.get("dg_sante_food_contact_materials"))),
        "Formula": escaped_text(clean_value(material.get("molecular_formula"))),
    }


def organoleptic_list_fields(material: dict) -> dict[str, str]:
    return {
        "Organoleptic Notes": render_descriptor_value(
            first_available(material, "organoleptic_notes", "description"),
            "Organoleptic",
        ),
        "Odor": render_descriptor_value(clean_value(material.get("odor")), "Organoleptic"),
        "Taste / Flavor": render_descriptor_value(clean_value(material.get("flavor")), "Organoleptic"),
        "Threshold": escaped_text(first_available(material, "threshold", "odor_threshold", "flavor_threshold")),
        "Occurrence": render_descriptor_value(clean_value(material.get("occurrence")), "Occurrence"),
        "Description": escaped_text(clean_value(material.get("description"))),
        "Synonyms": escaped_text(format_synonyms(material.get("synonyms"))),
    }


def render_descriptor_value(value: str, field: str) -> str:
    text = format_organoleptic_text(value)
    terms = descriptor_terms(text)
    chips = "".join(
        f'<a class="descriptor-chip" href="?q={quote(term)}&fields={quote(field)}">{escape(term)}</a>'
        for term in terms
    )
    if not terms:
        return escaped_text(text)
    return f'<div class="descriptor-group"><span class="descriptor-title">Raw</span>{escape(text)}</div><div class="descriptor-group"><span class="descriptor-title">Clickable Terms</span>{chips}</div>'


def escaped_text(value: str) -> str:
    return escape(clean_value(value))


def parse_fields_param(raw_fields: str | None) -> list[str]:
    if not raw_fields:
        return ["All fields"]
    fields = [field for field in raw_fields.split(",") if field in SEARCH_FIELD_GROUPS]
    if not fields or "All fields" in fields:
        return ["All fields"]
    return fields


def set_search_query_params(query: str, fields: list[str], page: int) -> None:
    params: dict[str, str] = {}
    if query:
        params["q"] = query
    if fields:
        params["fields"] = ",".join(fields)
    if page > 1:
        params["page"] = str(page)
    st.query_params.clear()
    for key, value in params.items():
        st.query_params[key] = value


def main() -> None:
    inject_styles()
    current_view = render_nav()

    if "selected_material" not in st.session_state:
        st.session_state.selected_material = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Identifier"
    if "search_fields" not in st.session_state:
        st.session_state.search_fields = parse_fields_param(st.query_params.get("fields"))
    if "page" not in st.session_state:
        st.session_state.page = int(st.query_params.get("page", "1") or "1")
    if "shelf" not in st.session_state:
        st.session_state.shelf = []

    if add_shelf_id := st.query_params.get("add_shelf"):
        if get_material(add_shelf_id) and add_shelf_id not in st.session_state.shelf:
            st.session_state.shelf.append(add_shelf_id)
        st.query_params.clear()
        st.query_params["view"] = "shelf"
        st.rerun()

    if st.query_params.get("q") or st.query_params.get("fields"):
        st.session_state.selected_material = None
        st.session_state.search_fields = parse_fields_param(st.query_params.get("fields"))
        st.session_state.page = int(st.query_params.get("page", "1") or "1")

    if current_view == "analytics":
        render_analytics()
        return
    if current_view == "shelf":
        render_shelf()
        return
    if current_view == "formulation":
        render_formulation_placeholder()
        return

    selected = st.query_params.get("material") or st.session_state.selected_material
    if selected:
        st.session_state.selected_material = selected
    if selected:
        material = get_material(selected)
        if material:
            render_detail(material)
            return
        st.session_state.selected_material = None

    render_hero()
    query_from_url = st.query_params.get("q", "")
    query = st.text_input(
        "Search",
        value=query_from_url,
        placeholder="Try ethyl maltol, caramel, rose, 111-70, FEMA 3487...",
    )
    if query != query_from_url:
        st.session_state.page = 1
        set_search_query_params(query, st.session_state.search_fields, 1)

    fields = render_field_filters(st.session_state.search_fields, query)
    results = search_materials(query, fields, limit=None)
    render_results(results, st.session_state.page, page_size=60)


if __name__ == "__main__":
    main()
