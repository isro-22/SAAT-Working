# SAAT Working

Launcher Streamlit untuk menjalankan 4 aplikasi SAAT dari 1 deployment.

Live app:
https://saat-working-aqfsogfaucx9qxhfr74anc.streamlit.app

## Aplikasi

| App | File utama | Fungsi |
| --- | --- | --- |
| 00 Chemicals DB | `00 Chemicals DB/app.py` | Pencarian dan manajemen database bahan kimia. |
| 01 Clean Database | `01 Clean Database/app.py` | Pembersihan, validasi, dan penataan database. |
| 02 BOM Breakdown | `02 BOM Breakdown/app/main.py` | Analisis breakdown Bill of Materials dan struktur produk. |
| 03 Formulation Sheet Creation | `03 Formulation Sheet Creation/app.py` | Pembuatan sheet formulasi dari template. |

## Entry Point

File utama deployment:

```text
streamlit_app.py
```

File `app.py` dan `index.py` tetap ada sebagai fallback jika konfigurasi Streamlit Cloud lama masih menunjuk ke salah satu file tersebut. Keduanya hanya meneruskan eksekusi ke `streamlit_app.py`.

## Struktur Utama

```text
SAAT Working/
├── streamlit_app.py
├── app.py
├── index.py
├── requirements.txt
├── README.md
├── apps/
│   └── _app_loader.py
├── 00 Chemicals DB/
├── 01 Clean Database/
├── 02 BOM Breakdown/
└── 03 Formulation Sheet Creation/
```

## Cara Kerja

`streamlit_app.py` menampilkan halaman launcher. User memilih salah satu aplikasi, lalu launcher memuat file app yang sesuai dengan bantuan `apps/_app_loader.py`.

Loader menambahkan path lokal app ke `sys.path`, menonaktifkan pemanggilan `st.set_page_config()` dari sub-app, dan membersihkan cache module lokal agar package dengan nama sama seperti `src` tidak bentrok antar app.

## Data Chemicals DB

File lengkap lokal `00 Chemicals DB/data/materials_final.json` berukuran besar dan tidak dipush ke GitHub. Untuk deployment, repo menyimpan versi kompresi:

```text
00 Chemicals DB/data/materials_final.json.gz
```

`00 Chemicals DB` akan membaca JSON asli jika tersedia lokal, lalu fallback ke file `.json.gz` saat berjalan di Streamlit Cloud.

## Jalankan Lokal

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Jika memakai virtual environment yang sudah ada:

```bash
.venv/bin/python -m streamlit run streamlit_app.py
```

## Deploy Streamlit Cloud

Gunakan konfigurasi berikut:

```text
Repository: isro-22/SAAT-Working
Branch: main
Main file path: streamlit_app.py
```

Jika Streamlit Cloud masih memakai `app.py` atau `index.py`, app tetap diarahkan ke launcher yang sama.
