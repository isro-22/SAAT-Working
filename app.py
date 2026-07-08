import os
import subprocess
import sys
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="SAAT Router", page_icon="🧭", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --bg: #07111f;
        --panel: rgba(15, 23, 42, 0.9);
        --text: #f8fafc;
        --muted: #94a3b8;
        --accent: #38bdf8;
        --accent-2: #818cf8;
    }
    .stApp {
        background: radial-gradient(circle at top left, rgba(56, 189, 248, 0.22), transparent 24%), linear-gradient(135deg, #07111f, #0f172a);
        color: var(--text);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .hero {
        padding: 1.2rem 1.4rem;
        border-radius: 20px;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 16px 40px rgba(0,0,0,0.25);
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin-bottom: 0.35rem;
    }
    .hero p {
        color: var(--muted);
        line-height: 1.6;
    }
    .card {
        padding: 1rem 1.1rem;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 28px rgba(0,0,0,0.2);
        height: 100%;
    }
    .card h3 {
        margin-top: 0;
        margin-bottom: 0.35rem;
    }
    .card p {
        color: var(--muted);
        line-height: 1.5;
    }
    .stSidebar {
        background: rgba(2, 6, 23, 0.95);
    }
    .stSidebar .stRadio > label {
        font-weight: 600;
        color: #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

APPS = [
    {
        "key": "chemicals",
        "title": "00 Chemicals DB",
        "icon": "🧪",
        "folder": "00 Chemicals DB",
        "description": "Aplikasi pencarian dan manajemen database bahan kimia.",
        "command": 'streamlit run "00 Chemicals DB/app.py"',
    },
    {
        "key": "clean",
        "title": "01 Clean Database",
        "icon": "🧼",
        "folder": "01 Clean Database",
        "description": "Alat pembersihan dan penataan database sebelum digunakan.",
        "command": 'streamlit run "01 Clean Database/app.py"',
    },
    {
        "key": "bom",
        "title": "02 BOM Breakdown",
        "icon": "🧰",
        "folder": "02 BOM Breakdown",
        "description": "Analisis breakdown Bill of Materials dan struktur produk.",
        "command": 'streamlit run "02 BOM Breakdown/app/main.py"',
    },
    {
        "key": "formulation",
        "title": "03 Formulation Sheet Creation",
        "icon": "📄",
        "folder": "03 Formulation Sheet Creation",
        "description": "Pembuatan sheet formulasi dengan template otomatis.",
        "command": 'streamlit run "03 Formulation Sheet Creation/app.py"',
    },
]

with st.sidebar:
    st.image("https://www.streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=140)
    st.title("SAAT Router")
    st.caption("Pusat navigasi aplikasi Streamlit")
    selected_key = st.radio(
        "Pilih modul",
        [app["key"] for app in APPS],
        format_func=lambda key: next(f"{app['icon']} {app['title']}" for app in APPS if app["key"] == key),
        horizontal=False,
    )

st.markdown('<div class="hero"><h1>SAAT Working Apps</h1><p>Portal utama untuk mengakses berbagai aplikasi Streamlit di workspace ini. Pilih modul pada sidebar untuk melihat detail dan tombol aksi langsung.</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 0.8])
with col1:
    st.subheader("Ringkasan")
    st.write("Aplikasi ini berfungsi sebagai router sentral sehingga semua folder aplikasi bisa diakses dari satu tempat yang terintegrasi dengan Streamlit.")
    st.info("Gunakan menu di sidebar untuk berpindah antar modul.")

with col2:
    st.subheader("Cara menjalankan")
    st.code('streamlit run app.py', language="bash")

selected_app = next(app for app in APPS if app["key"] == selected_key)

st.markdown(
    f"""
    <div class='card'>
        <h3>{selected_app['icon']} {selected_app['title']}</h3>
        <p>{selected_app['description']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.subheader("Detail aplikasi")
col_a, col_b = st.columns(2)
with col_a:
    st.write(f"**Folder:** {selected_app['folder']}")
    st.write(f"**Tujuan:** {selected_app['description']}")
with col_b:
    st.write("**Perintah run:")
    st.code(selected_app["command"], language="bash")

st.write("")
col_open, col_folder = st.columns(2)
with col_open:
    if st.button("Open App", use_container_width=True):
        app_path = Path(selected_app["folder"]) / "app.py"
        if selected_app["key"] == "bom":
            app_path = Path(selected_app["folder"]) / "app" / "main.py"
        if app_path.exists():
            target_dir = str(app_path.parent.resolve())
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(app_path)], cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            st.success("Aplikasi sedang dibuka di background.")
        else:
            st.error("File aplikasi tidak ditemukan.")
with col_folder:
    st.info(f"Folder: {selected_app['folder']}")

st.write("")
st.caption("Router ini dibuat agar tampilan utama lebih modern dan dapat dipakai sebagai halaman awal saat aplikasi Streamlit dijalankan.")
