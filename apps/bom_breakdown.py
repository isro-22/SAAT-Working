import streamlit as st

from apps._app_loader import load_and_run_app


def render_bom_breakdown() -> None:
    try:
        load_and_run_app("02 BOM Breakdown/app/main.py")
    except Exception as exc:
        st.error(f"Gagal memuat 02 BOM Breakdown: {exc}")
