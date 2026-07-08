from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from uuid import uuid4

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]


def _app_root_for_path(app_path: Path) -> Path:
    if app_path.parent.name == "app":
        return app_path.parent.parent
    return app_path.parent


def load_and_run_app(relative_app_path: str, module_name: str | None = None) -> None:
    app_path = ROOT / relative_app_path
    if not app_path.exists():
        raise FileNotFoundError(f"App file not found: {app_path}")

    app_root = _app_root_for_path(app_path)
    if module_name is None:
        module_name = f"__loaded_app__{app_path.stem}_{uuid4().hex}"

    original_set_page_config = st.set_page_config
    sys.path.insert(0, str(app_root))
    try:
        st.set_page_config = lambda *args, **kwargs: None
        spec = importlib.util.spec_from_file_location(module_name, app_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {app_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        if hasattr(module, "main") and callable(getattr(module, "main")):
            module.main()
    finally:
        st.set_page_config = original_set_page_config
        if sys.path and sys.path[0] == str(app_root):
            sys.path.pop(0)
