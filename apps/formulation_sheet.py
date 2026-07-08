import streamlit as st

from apps._app_loader import load_and_run_app


def render_formulation_sheet() -> None:
    try:
        load_and_run_app("03 Formulation Sheet Creation/app.py")
    except Exception as exc:
        st.error(f"Gagal memuat 03 Formulation Sheet Creation: {exc}")
