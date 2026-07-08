from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

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


def page_runner(relative_path: str) -> Callable[[], None]:
    def run() -> None:
        load_and_run_app(relative_path)

    return run


st.set_page_config(page_title="SAAT Working", layout="wide")

pages = discover_app_pages()

if not pages:
    st.title("SAAT Working")
    st.warning("Tidak ada aplikasi yang ditemukan.")
else:
    navigation = {
        "Menu Aplikasi": [
            st.Page(page_runner(page.relative_path), title=page.title)
            for page in pages
        ]
    }

    selected_page = st.navigation(navigation)
    selected_page.run()
