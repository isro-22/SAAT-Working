from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from apps._app_loader import load_and_run_app


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class AppPage:
    title: str
    relative_path: str
    description: str


APP_DESCRIPTIONS = {
    "00 Chemicals DB": "Pencarian dan manajemen database bahan kimia.",
    "01 Clean Database": "Pembersihan, validasi, dan penataan database.",
    "02 BOM Breakdown": "Analisis breakdown Bill of Materials dan struktur produk.",
    "03 Formulation Sheet Creation": "Pembuatan sheet formulasi dari template.",
}


def discover_app_pages() -> list[AppPage]:
    pages: list[AppPage] = []
    for folder in sorted(path for path in ROOT.iterdir() if path.is_dir()):
        if folder.name.startswith(".") or folder.name in {"apps", "__pycache__"}:
            continue

        candidates = [folder / "app.py", folder / "app" / "main.py"]
        app_file = next((candidate for candidate in candidates if candidate.exists()), None)
        if app_file is None:
            continue

        pages.append(
            AppPage(
                title=folder.name,
                relative_path=app_file.relative_to(ROOT).as_posix(),
                description=APP_DESCRIPTIONS.get(
                    folder.name,
                    "Aplikasi Streamlit dalam workspace SAAT Working.",
                ),
            )
        )
    return pages


def open_app(app_title: str) -> None:
    st.session_state.selected_app = app_title
    st.rerun()


def back_to_home() -> None:
    st.session_state.selected_app = None
    st.rerun()


def render_launcher(pages: list[AppPage]) -> None:
    st.title("SAAT Working")
    st.caption("Pilih aplikasi yang ingin dijalankan dari satu deployment Streamlit.")

    columns = st.columns(2)
    for index, page in enumerate(pages):
        with columns[index % 2]:
            with st.container(border=True):
                st.subheader(page.title)
                st.write(page.description)
                st.caption(page.relative_path)
                if st.button(f"Buka {page.title}", key=f"open_{page.title}", use_container_width=True):
                    open_app(page.title)


def render_selected_app(page: AppPage) -> None:
    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("Kembali", use_container_width=True):
            back_to_home()
    with col_title:
        st.subheader(page.title)

    try:
        load_and_run_app(page.relative_path)
    except Exception as exc:
        st.error(f"Gagal memuat {page.title}: {exc}")


st.set_page_config(page_title="SAAT Working", layout="wide")

pages = discover_app_pages()
page_by_title = {page.title: page for page in pages}

if "selected_app" not in st.session_state:
    st.session_state.selected_app = None

if not pages:
    st.title("SAAT Working")
    st.warning("Tidak ada aplikasi yang ditemukan.")
elif st.session_state.selected_app is None:
    render_launcher(pages)
else:
    selected_page = page_by_title.get(st.session_state.selected_app)
    if selected_page is None:
        back_to_home()
    else:
        render_selected_app(selected_page)
