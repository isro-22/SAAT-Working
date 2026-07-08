# Deploy ke Streamlit Community Cloud

## File utama
- Entry point aplikasi: index.py

## Requirements
- requirements.txt

## Langkah deploy
1. Push project ke GitHub repository private.
2. Buka https://share.streamlit.io/
3. Pilih "New app".
4. Pilih repository private Anda.
5. Tentukan:
   - Branch: main
   - Main file path: index.py
6. Klik Deploy.

## Catatan
- Jika aplikasi memanggil file lain di folder proyek, pastikan path relatif benar.
- Untuk modul yang membuka aplikasi lain, gunakan tombol Open App yang memanggil Streamlit secara terpisah.
