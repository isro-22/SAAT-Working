import streamlit as st

from apps._app_loader import load_and_run_app


def render_chemicals_db() -> None:
    try:
        load_and_run_app("00 Chemicals DB/app.py")
    except Exception as exc:
        st.error(f"Gagal memuat 00 Chemicals DB: {exc}")
