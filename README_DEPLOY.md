# Deploy ke Streamlit Community Cloud

## File utama
- Entry point aplikasi: `streamlit_app.py`

## Requirements
- `requirements.txt`

## Langkah deploy
1. Push project ke GitHub repository private.
2. Buka https://share.streamlit.io/
3. Pilih "New app".
4. Pilih repository private Anda.
5. Tentukan:
   - Branch: `main`
   - Main file path: `streamlit_app.py`
6. Klik Deploy.

## Catatan
- `streamlit_app.py` adalah launcher yang menampilkan pilihan aplikasi lalu memuat aplikasi terpilih dalam satu deployment.
- Aplikasi lain tidak dijalankan sebagai proses terpisah, sehingga Streamlit Cloud dapat menampilkan semua modul dari satu deployment.
- Jika ada error dependensi, pastikan `requirements.txt` mencakup semua paket yang digunakan oleh setiap sub-aplikasi.
