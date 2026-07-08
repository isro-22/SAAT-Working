import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def launch_streamlit_app(relative_app_path: str, port: int) -> tuple[str, str]:
    app_path = ROOT / relative_app_path
    if not app_path.exists():
        raise FileNotFoundError(f"App file not found: {app_path}")

    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(ROOT))

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
        "--server.headless",
        "true",
    ]

    subprocess.Popen(
        command,
        cwd=str(app_path.parent),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    return f"http://localhost:{port}", str(app_path)
