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


def _sys_paths_for_app(app_path: Path) -> list[str]:
    paths = [str(app_path.parent)]
    app_root = _app_root_for_path(app_path)
    if app_root != app_path.parent:
        paths.append(str(app_root))
    return paths


def _local_module_names(paths: list[str]) -> set[str]:
    module_names: set[str] = set()
    for path in paths:
        root = Path(path)
        if not root.exists():
            continue
        for child in root.iterdir():
            if child.name.startswith(".") or child.name == "__pycache__":
                continue
            if child.is_file() and child.suffix == ".py" and child.stem != "__init__":
                module_names.add(child.stem)
            elif child.is_dir() and (child / "__init__.py").exists():
                module_names.add(child.name)
    return module_names


def _clear_local_modules(module_names: set[str]) -> None:
    for module_name in module_names:
        for loaded_name in list(sys.modules):
            if loaded_name == module_name or loaded_name.startswith(f"{module_name}."):
                sys.modules.pop(loaded_name, None)


def load_and_run_app(relative_app_path: str, module_name: str | None = None) -> None:
    app_path = ROOT / relative_app_path
    if not app_path.exists():
        raise FileNotFoundError(f"App file not found: {app_path}")

    app_paths = _sys_paths_for_app(app_path)
    local_module_names = _local_module_names(app_paths)
    if module_name is None:
        module_name = f"__loaded_app__{app_path.stem}_{uuid4().hex}"

    original_set_page_config = st.set_page_config
    for path in reversed(app_paths):
        sys.path.insert(0, path)
    try:
        _clear_local_modules(local_module_names)
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
        for path in app_paths:
            if sys.path and sys.path[0] == path:
                sys.path.pop(0)
            elif path in sys.path:
                sys.path.remove(path)
