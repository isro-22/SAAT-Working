import streamlit as st

from apps.chemicals_db import render_chemicals_db
from apps.clean_database import render_clean_database
from apps.bom_breakdown import render_bom_breakdown
from apps.formulation_sheet import render_formulation_sheet


PAGES = {
    "00 Chemicals DB": render_chemicals_db,
    "01 Clean Database": render_clean_database,
    "02 BOM Breakdown": render_bom_breakdown,
    "03 Formulation Sheet Creation": render_formulation_sheet,
}


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
        selection = st.radio("Pilih aplikasi", list(PAGES.keys()))
        st.markdown("---")
        st.write("Tambahkan modul baru ke folder apps/ lalu daftarkan di sini.")

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
            <strong>{selection}</strong><br>
            Pilih modul di sidebar untuk melihat detail aplikasi dan tombol aksi.
        </div>
        """,
        unsafe_allow_html=True,
    )

    PAGES[selection]()


if __name__ == "__main__":
    main()
