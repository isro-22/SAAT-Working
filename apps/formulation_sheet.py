import streamlit as st

from apps.launcher import launch_streamlit_app


def render_formulation_sheet() -> None:
    st.markdown(
        """
        <div style="padding: 1rem 1.1rem; border-radius: 18px; background: rgba(255,255,255,0.8); border: 1px solid #d2d2d7; box-shadow: 0 8px 24px rgba(0,0,0,0.04);">
            <h3 style="margin:0 0 0.3rem; color:#1d1d1f;">03 Formulation Sheet Creation</h3>
            <p style="margin:0; color:#6e6e73;">Aplikasi untuk membuat sheet formulasi dengan template otomatis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("Open App", use_container_width=True):
        try:
            url, _ = launch_streamlit_app("03 Formulation Sheet Creation/app.py", 8506)
            st.success(f"Aplikasi dibuka di {url}")
        except Exception as exc:
            st.error(f"Gagal menjalankan aplikasi: {exc}")

    st.code('streamlit run "03 Formulation Sheet Creation/app.py"', language="bash")
