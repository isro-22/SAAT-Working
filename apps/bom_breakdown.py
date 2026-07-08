import streamlit as st

from apps.launcher import launch_streamlit_app


def render_bom_breakdown() -> None:
    st.markdown(
        """
        <div style="padding: 1rem 1.1rem; border-radius: 18px; background: rgba(255,255,255,0.8); border: 1px solid #d2d2d7; box-shadow: 0 8px 24px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 0.3rem; color:#1d1d1f;">02 BOM Breakdown</h3>
            <p style="margin:0; color:#6e6e73;">Aplikasi untuk analisis breakdown Bill of Materials dan struktur produk.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("Open App", use_container_width=True):
        try:
            url, _ = launch_streamlit_app("02 BOM Breakdown/app/main.py", 8505)
            st.success(f"Aplikasi dibuka di {url}")
        except Exception as exc:
            st.error(f"Gagal menjalankan aplikasi: {exc}")

    st.code('streamlit run "02 BOM Breakdown/app/main.py"', language="bash")
