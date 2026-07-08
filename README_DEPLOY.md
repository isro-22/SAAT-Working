# Deploy ke Streamlit Community Cloud

## File utama
- Entry point aplikasi: `index.py`

## Requirements
- `requirements.txt`

## Langkah deploy
1. Push project ke GitHub repository private.
2. Buka https://share.streamlit.io/
3. Pilih "New app".
4. Pilih repository private Anda.
5. Tentukan:
   - Branch: `main`
   - Main file path: `index.py`
6. Klik Deploy.

## Catatan
- `index.py` adalah router yang memuat setiap aplikasi secara internal.
- Aplikasi lain tidak dijalankan sebagai proses terpisah, sehingga Streamlit Cloud dapat menampilkan semua modul dari satu deployment.
- Jika ada error dependensi, pastikan `requirements.txt` mencakup semua paket yang digunakan oleh setiap sub-aplikasi.
