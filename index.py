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
            )
        )
    return pages


PAGES = discover_app_pages()


def main() -> None:
    st.set_page_config(page_title="SAAT Streamlit Hub", page_icon="🧭", layout="wide")

    st.markdown(
        """
        <style>
        :root {
            --bg: #f5f5f7;
            --panel: rgba(255,255,255,0.8);
            --text: #1d1d1f;
            --muted: #6e6e73;
            --line: #d2d2d7;
            --accent: #0071e3;
        }
        .stApp {
            background: linear-gradient(135deg, #f5f5f7 0%, #ffffff 100%);
            color: var(--text);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stSidebar {
            background: #f5f5f7;
            border-right: 1px solid var(--line);
        }
        .stSidebar .stRadio > label, .stSidebar h1, .stSidebar p {
            color: var(--text);
        }
        .hero {
            padding: 1.4rem 1.5rem;
            border-radius: 24px;
            background: var(--panel);
            border: 1px solid var(--line);
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0 0 0.35rem;
            font-size: 2rem;
            color: var(--text);
        }
        .hero p {
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
        }
        .card {
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: var(--panel);
            border: 1px solid var(--line);
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("SAAT Streamlit")
        st.caption("Struktur multipage dengan index.py dan folder apps/")
        if not PAGES:
            st.warning("Tidak ada aplikasi yang ditemukan.")
            return
        selection = st.radio(
            "Pilih aplikasi",
            PAGES,
            format_func=lambda page: page.title,
        )
        st.markdown("---")
        st.write("Aplikasi dibaca otomatis dari folder yang memiliki app.py atau app/main.py.")

    st.markdown(
        """
        <div class="hero">
            <h1>SAAT Working Apps</h1>
            <p>Portal utama yang menampilkan berbagai aplikasi Streamlit dengan tampilan elegan dan modern.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card">
            <strong>{selection.title}</strong><br>
            Path: <code>{selection.relative_path}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        load_and_run_app(selection.relative_path)
    except Exception as exc:
        st.error(f"Gagal memuat {selection.title}: {exc}")


if __name__ == "__main__":
    main()
