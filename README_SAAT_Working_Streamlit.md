# SAAT Working - 1 Deployment untuk 4 App Streamlit

README ini menjelaskan cara menjalankan 4 folder aplikasi Streamlit dalam 1 deployment utama.  
Konsepnya sederhana: setiap folder tetap berisi app masing-masing, lalu 1 file utama di root project menjadi router atau menu utama.

---

## 1. Tujuan

Project ini dibuat agar 4 aplikasi Streamlit dapat dijalankan dari 1 deployment saja.

Dengan struktur ini, user cukup membuka 1 link Streamlit.  
Di dalamnya tersedia menu untuk memilih app yang ingin digunakan.

---

## 2. Struktur Folder yang Disarankan

Gunakan struktur seperti berikut.

```text
SAAT Working/
│
├── streamlit_app.py
├── requirements.txt
├── README.md
│
├── app_1/
│   └── app.py
│
├── app_2/
│   └── app.py
│
├── app_3/
│   └── app.py
│
└── app_4/
    └── app.py
```

Keterangan:

- `streamlit_app.py` adalah file utama yang dijalankan saat deploy.
- `requirements.txt` berisi daftar library Python yang dibutuhkan.
- `app_1`, `app_2`, `app_3`, dan `app_4` adalah folder aplikasi.
- Setiap folder app memiliki file utama, misalnya `app.py`.

Jika nama folder berbeda, cukup sesuaikan path di file `streamlit_app.py`.

---

## 3. File Utama Router

Buat file `streamlit_app.py` di root folder `SAAT Working`.

```python
import streamlit as st

st.set_page_config(
    page_title="SAAT Working",
    layout="wide"
)

st.title("SAAT Working")
st.caption("Satu deployment untuk menjalankan beberapa aplikasi Streamlit.")

pages = {
    "Menu Aplikasi": [
        st.Page("app_1/app.py", title="App 1"),
        st.Page("app_2/app.py", title="App 2"),
        st.Page("app_3/app.py", title="App 3"),
        st.Page("app_4/app.py", title="App 4"),
    ]
}

selected_page = st.navigation(pages)
selected_page.run()
```

Ganti bagian ini sesuai nama folder asli:

```python
st.Page("app_1/app.py", title="App 1")
st.Page("app_2/app.py", title="App 2")
st.Page("app_3/app.py", title="App 3")
st.Page("app_4/app.py", title="App 4")
```

Contoh jika folder asli bernama:

```text
dashboard_sales/
prediksi_data/
upload_excel/
laporan_final/
```

Maka router menjadi:

```python
pages = {
    "Menu Aplikasi": [
        st.Page("dashboard_sales/app.py", title="Dashboard Sales"),
        st.Page("prediksi_data/app.py", title="Prediksi Data"),
        st.Page("upload_excel/app.py", title="Upload Excel"),
        st.Page("laporan_final/app.py", title="Laporan Final"),
    ]
}
```

---

## 4. Penyesuaian pada Setiap App

Setiap app tetap boleh memakai kode Streamlit seperti biasa.

Contoh isi `app_1/app.py`:

```python
import streamlit as st

st.header("App 1")
st.write("Ini adalah halaman App 1.")
```

Contoh isi `app_2/app.py`:

```python
import streamlit as st

st.header("App 2")
st.write("Ini adalah halaman App 2.")
```

Penting:

Jangan menaruh `st.set_page_config()` di setiap file app.  
Cukup letakkan `st.set_page_config()` di `streamlit_app.py`.

Jika `st.set_page_config()` masih ada di file app lain, hapus atau komentari agar tidak terjadi error.

---

## 5. Mengatur Path File Data

Jika app membaca file seperti CSV, Excel, gambar, atau model, gunakan path yang aman.

Contoh yang disarankan:

```python
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "data.xlsx"

df = pd.read_excel(DATA_PATH)
```

Jangan terlalu bergantung pada path seperti ini:

```python
pd.read_excel("data/data.xlsx")
```

Path tersebut bisa error saat app dijalankan dari router utama.

---

## 6. File requirements.txt

Buat file `requirements.txt` di root folder.

Contoh isi awal:

```text
streamlit>=1.36
pandas
numpy
openpyxl
plotly
matplotlib
scikit-learn
```

Sesuaikan dengan library yang benar-benar dipakai oleh app.

Contoh:

- Jika app membaca Excel, gunakan `openpyxl`.
- Jika app memakai grafik Plotly, gunakan `plotly`.
- Jika app memakai model machine learning, gunakan `scikit-learn`.
- Jika app memakai database, tambahkan library database yang sesuai.

Jangan masukkan library bawaan Python seperti:

```text
os
sys
math
datetime
pathlib
json
random
```

Library tersebut sudah tersedia di Python.

---

## 7. Cara Menjalankan di Lokal

Masuk ke folder project.

```bash
cd "SAAT Working"
```

Buat virtual environment.

```bash
python -m venv .venv
```

Aktifkan virtual environment.

Untuk Windows:

```bash
.venv\Scripts\activate
```

Untuk macOS atau Linux:

```bash
source .venv/bin/activate
```

Install dependency.

```bash
pip install -r requirements.txt
```

Jalankan app utama.

```bash
streamlit run streamlit_app.py
```

Setelah itu, buka link lokal yang muncul di terminal.

Biasanya:

```text
http://localhost:8501
```

---

## 8. Cara Deploy ke Streamlit Community Cloud

Langkah deployment:

1. Upload semua folder project ke GitHub.
2. Pastikan file `streamlit_app.py` berada di root project.
3. Pastikan file `requirements.txt` berada di root project.
4. Buka Streamlit Community Cloud.
5. Pilih repository GitHub.
6. Pada bagian main file path, isi:

```text
streamlit_app.py
```

Jika folder `SAAT Working` berada di dalam repository, isi main file path seperti ini:

```text
SAAT Working/streamlit_app.py
```

7. Klik Deploy.

---

## 9. Contoh Struktur Siap Deploy

Contoh struktur final:

```text
SAAT Working/
│
├── streamlit_app.py
├── requirements.txt
├── README.md
│
├── dashboard/
│   ├── app.py
│   └── data/
│       └── data_dashboard.xlsx
│
├── klasifikasi/
│   ├── app.py
│   └── model/
│       └── model.pkl
│
├── visualisasi/
│   ├── app.py
│   └── assets/
│       └── logo.png
│
└── laporan/
    ├── app.py
    └── template/
        └── template_laporan.xlsx
```

Contoh `streamlit_app.py` untuk struktur di atas:

```python
import streamlit as st

st.set_page_config(
    page_title="SAAT Working",
    layout="wide"
)

st.title("SAAT Working")
st.caption("Pilih aplikasi dari menu yang tersedia.")

pages = {
    "Menu Aplikasi": [
        st.Page("dashboard/app.py", title="Dashboard"),
        st.Page("klasifikasi/app.py", title="Klasifikasi"),
        st.Page("visualisasi/app.py", title="Visualisasi"),
        st.Page("laporan/app.py", title="Laporan"),
    ]
}

selected_page = st.navigation(pages)
selected_page.run()
```

---

## 10. Troubleshooting

### Error: file app tidak ditemukan

Periksa path di `st.Page()`.

Contoh salah:

```python
st.Page("app1.py", title="App 1")
```

Contoh benar jika file berada dalam folder:

```python
st.Page("app_1/app.py", title="App 1")
```

---

### Error karena nama folder mengandung spasi

Sebaiknya gunakan nama folder tanpa spasi.

Contoh tidak disarankan:

```text
App Satu/
```

Contoh disarankan:

```text
app_satu/
```

Jika folder memakai spasi, path bisa tetap bekerja, tetapi lebih rawan error saat import, deploy, atau membaca file.

---

### Error karena `st.set_page_config()`

Jika muncul error terkait `st.set_page_config()`, pastikan hanya file `streamlit_app.py` yang memakai kode berikut:

```python
st.set_page_config(
    page_title="SAAT Working",
    layout="wide"
)
```

Hapus `st.set_page_config()` dari file app lain.

---

### Error saat membaca file Excel, CSV, gambar, atau model

Gunakan `Path(__file__)`.

Contoh:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "data" / "file.xlsx"
```

---

### Error karena library belum terinstall

Tambahkan library tersebut ke `requirements.txt`, lalu deploy ulang.

Contoh:

```text
pandas
openpyxl
plotly
```

---

## 11. Catatan Penting

- Jangan menjalankan 4 app dengan 4 command `streamlit run`.
- Cukup jalankan 1 file utama, yaitu `streamlit_app.py`.
- File utama bertugas sebagai router.
- Setiap folder app tetap berdiri sendiri.
- Semua dependency harus berada di 1 file `requirements.txt`.
- Saat deploy, pilih `streamlit_app.py` sebagai main file.

---

## 12. Ringkasan

Dengan struktur ini, project `SAAT Working` dapat menjalankan 4 aplikasi Streamlit dalam 1 deployment.

Alur kerjanya:

```text
User membuka 1 link Streamlit
        ↓
streamlit_app.py berjalan
        ↓
User memilih menu app
        ↓
App dari folder yang dipilih dijalankan
```

Hasil akhir:

- 1 repository
- 1 deployment
- 1 link aplikasi
- 4 app Streamlit dalam 1 sistem
