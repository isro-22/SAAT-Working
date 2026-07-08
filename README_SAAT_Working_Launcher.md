# SAAT Working - 1 Deployment untuk 4 App Streamlit dengan Konsep Launcher

README ini menjelaskan cara menjalankan 4 folder aplikasi Streamlit dalam 1 deployment utama, tetapi tampilannya dibuat seperti membuka app baru, bukan seperti multipage biasa.

Konsepnya:

```text
User membuka 1 link Streamlit
        ↓
Muncul halaman launcher
        ↓
User memilih salah satu app
        ↓
Streamlit menjalankan file app.py dari folder yang dipilih
```

Secara teknis, ini tetap berjalan dalam 1 deployment Streamlit.  
Namun dari sisi tampilan, user akan merasa memilih aplikasi yang berbeda.

---

## 1. Tujuan

Project ini dibuat agar 4 aplikasi Streamlit dapat dijalankan dari 1 link deployment.

Pendekatan ini cocok jika:

- Setiap app berada dalam folder berbeda.
- Setiap app punya alur kerja sendiri.
- Tidak ingin memakai menu multipage bawaan Streamlit.
- Ingin tampilan awal seperti dashboard pemilih aplikasi.
- Ingin cukup deploy 1 app utama saja.

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

- `streamlit_app.py` adalah file utama untuk deployment.
- `requirements.txt` berisi semua library yang dipakai oleh 4 app.
- `app_1`, `app_2`, `app_3`, dan `app_4` adalah folder aplikasi.
- Setiap folder memiliki file utama bernama `app.py`.

Jika nama folder berbeda, ubah path di bagian konfigurasi app.

---

## 3. File Utama Launcher

Buat file `streamlit_app.py` di root folder `SAAT Working`.

```python
import streamlit as st
from pathlib import Path
import runpy

st.set_page_config(
    page_title="SAAT Working",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

APPS = {
    "App 1": {
        "path": BASE_DIR / "app_1" / "app.py",
        "description": "Deskripsi singkat untuk App 1."
    },
    "App 2": {
        "path": BASE_DIR / "app_2" / "app.py",
        "description": "Deskripsi singkat untuk App 2."
    },
    "App 3": {
        "path": BASE_DIR / "app_3" / "app.py",
        "description": "Deskripsi singkat untuk App 3."
    },
    "App 4": {
        "path": BASE_DIR / "app_4" / "app.py",
        "description": "Deskripsi singkat untuk App 4."
    },
}

if "selected_app" not in st.session_state:
    st.session_state.selected_app = None


def open_app(app_name):
    st.session_state.selected_app = app_name
    st.rerun()


def back_to_home():
    st.session_state.selected_app = None
    st.rerun()


if st.session_state.selected_app is None:
    st.title("SAAT Working")
    st.write("Pilih aplikasi yang ingin dijalankan.")

    cols = st.columns(2)

    for index, (app_name, app_info) in enumerate(APPS.items()):
        with cols[index % 2]:
            with st.container(border=True):
                st.subheader(app_name)
                st.write(app_info["description"])

                if st.button(f"Buka {app_name}", key=f"btn_{app_name}"):
                    open_app(app_name)

else:
    selected_app = st.session_state.selected_app
    app_path = APPS[selected_app]["path"]

    col1, col2 = st.columns([1, 6])

    with col1:
        if st.button("← Kembali"):
            back_to_home()

    with col2:
        st.subheader(selected_app)

    if app_path.exists():
        runpy.run_path(str(app_path), run_name="__main__")
    else:
        st.error(f"File app tidak ditemukan: {app_path}")
```

---

## 4. Cara Mengganti Nama App

Ubah bagian `APPS` di file `streamlit_app.py`.

Contoh jika nama folder asli seperti ini:

```text
dashboard_sales/
prediksi_data/
upload_excel/
laporan_final/
```

Maka bagian `APPS` menjadi:

```python
APPS = {
    "Dashboard Sales": {
        "path": BASE_DIR / "dashboard_sales" / "app.py",
        "description": "Menampilkan ringkasan data penjualan."
    },
    "Prediksi Data": {
        "path": BASE_DIR / "prediksi_data" / "app.py",
        "description": "Menjalankan proses prediksi berdasarkan data input."
    },
    "Upload Excel": {
        "path": BASE_DIR / "upload_excel" / "app.py",
        "description": "Mengunggah dan membaca data dari file Excel."
    },
    "Laporan Final": {
        "path": BASE_DIR / "laporan_final" / "app.py",
        "description": "Membuat laporan akhir berdasarkan data yang tersedia."
    },
}
```

---

## 5. Penyesuaian pada Setiap Folder App

Setiap folder app tetap bisa berisi kode Streamlit sendiri.

Contoh isi `app_1/app.py`:

```python
import streamlit as st

st.header("App 1")
st.write("Ini adalah isi App 1.")
```

Contoh isi `app_2/app.py`:

```python
import streamlit as st

st.header("App 2")
st.write("Ini adalah isi App 2.")
```

---

## 6. Hal Penting agar Tidak Error

### 6.1 Jangan Pakai `st.set_page_config()` di Setiap App

Cukup pakai `st.set_page_config()` di `streamlit_app.py`.

Hapus kode seperti ini dari file app lain:

```python
st.set_page_config(...)
```

Jika kode tersebut tetap ada di `app_1/app.py`, `app_2/app.py`, dan lainnya, Streamlit bisa menampilkan error.

---

### 6.2 Gunakan Path yang Aman untuk File Data

Jika app membaca file Excel, CSV, gambar, atau model, gunakan `Path(__file__)`.

Contoh:

```python
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "data.xlsx"

df = pd.read_excel(DATA_PATH)
```

Jangan hanya memakai:

```python
df = pd.read_excel("data/data.xlsx")
```

Path tersebut bisa error saat app dijalankan dari file launcher.

---

### 6.3 Hindari Nama Folder dengan Spasi

Sebaiknya gunakan nama folder seperti ini:

```text
app_1
dashboard_sales
prediksi_data
laporan_final
```

Hindari nama folder seperti ini:

```text
App 1
Dashboard Sales
Laporan Final
```

Folder dengan spasi tetap bisa berjalan, tetapi lebih rawan error saat import, deploy, atau membaca file.

---

## 7. File requirements.txt

Buat file `requirements.txt` di root folder.

Contoh:

```text
streamlit>=1.36
pandas
numpy
openpyxl
plotly
matplotlib
scikit-learn
```

Sesuaikan dengan library yang dipakai oleh semua app.

Jangan masukkan library bawaan Python seperti:

```text
os
sys
json
math
datetime
pathlib
random
```

Library tersebut sudah tersedia di Python.

---

## 8. Cara Menjalankan di Lokal

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

Buka link lokal yang muncul di terminal.

Biasanya:

```text
http://localhost:8501
```

---

## 9. Cara Deploy ke Streamlit Community Cloud

Langkah deployment:

1. Upload seluruh folder project ke GitHub.
2. Pastikan `streamlit_app.py` berada di root folder project.
3. Pastikan `requirements.txt` berada di root folder project.
4. Buka Streamlit Community Cloud.
5. Pilih repository GitHub.
6. Isi main file path dengan:

```text
streamlit_app.py
```

Jika project berada dalam folder `SAAT Working`, isi:

```text
SAAT Working/streamlit_app.py
```

7. Klik Deploy.

---

## 10. Batasan Pendekatan Launcher

Pendekatan ini membuat app terasa seperti app berbeda, tetapi tetap berjalan dalam 1 proses Streamlit.

Artinya:

- URL tetap 1.
- Deployment tetap 1.
- Semua app memakai environment dependency yang sama.
- Semua app memakai session Streamlit yang sama.
- Tidak ada 4 server Streamlit yang benar-benar terpisah.

Jika ingin benar-benar menjadi 4 app terpisah, maka perlu 4 deployment berbeda atau menggunakan server sendiri dengan reverse proxy seperti Nginx.

---

## 11. Jika Ingin 4 App Benar-Benar Terpisah

Jika ingin setiap app punya link sendiri, gunakan struktur seperti ini dalam 1 repository:

```text
SAAT Working/
│
├── requirements.txt
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

Lalu buat 4 deployment di Streamlit Community Cloud:

```text
Deployment 1: app_1/app.py
Deployment 2: app_2/app.py
Deployment 3: app_3/app.py
Deployment 4: app_4/app.py
```

Kelebihannya:

- Setiap app punya link sendiri.
- Setiap app terasa benar-benar mandiri.
- Error di satu app tidak langsung mengganggu app lain.

Kekurangannya:

- Deployment menjadi 4.
- Link menjadi 4.
- Pengaturan harus dilakukan per app.

---

## 12. Kesimpulan

Jika ingin cukup 1 deployment dan 1 link, gunakan konsep launcher.

File utama:

```text
streamlit_app.py
```

Isi utamanya:

```text
Menampilkan daftar app
Menyimpan app yang dipilih
Menjalankan app.py dari folder yang dipilih
```

Jika ingin 4 app benar-benar terpisah, gunakan 4 deployment berbeda.

Rekomendasi untuk project ini:

```text
Gunakan 1 deployment dengan konsep launcher.
```

Pendekatan ini paling sesuai jika tujuan utamanya adalah menjalankan 4 folder app dari 1 link Streamlit.
