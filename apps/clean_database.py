import streamlit as st

from apps._app_loader import load_and_run_app


def render_clean_database() -> None:
    try:
        load_and_run_app("01 Clean Database/app.py")
    except Exception as exc:
        st.error(f"Gagal memuat 01 Clean Database: {exc}")
