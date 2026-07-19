# Architecture

## Overview

Project ini adalah aplikasi Streamlit untuk eksplorasi database flavor chemical lokal. Entry point tipis berada di `app.py`, UI utama di `src/flavor_db/app.py`, dan semua akses data melewati `src/flavor_db/data_engine.py`.

## Runtime Flow

1. Streamlit menjalankan `app.py`.
2. `app.py` memanggil `src.flavor_db.app.main()`.
3. UI memanggil data engine untuk search, detail, analytics, similar materials, dan shelf comparison.
4. Data engine membaca file lokal `.json` atau `.json.gz`, lalu menahan dataset dan indeks di memory cache.

## Data Boundary

Semua pembacaan material harus melewati fungsi di `data_engine.py`.

- `resolve_material_data_file()` menentukan file data aktif.
- `read_json_records()` membaca `.json` dan `.json.gz`.
- `load_materials()` menjadi cache utama dataset.
- `_search_index()` menjadi cache teks pencarian.
- `_material_lookup()` menjadi cache identifier lookup.
- `_sorted_materials()` menjadi cache urutan default untuk home/list page.

## Ponytail Approach

Project ini mengikuti prinsip `DietrichGebert/ponytail`: sederhanakan implementasi, manfaatkan library standar Python sebelum menambah dependency, dan simpan abstraksi hanya ketika mengurangi duplikasi nyata.

Efeknya pada implementasi:

- Tidak menambah package untuk membaca gzip karena `gzip` dan `json` dari stdlib sudah cukup.
- Loader `.json` dan `.json.gz` digabung dalam satu fungsi.
- Sorting dan lookup dicache agar lebih cepat tanpa mengubah kontrak UI.
- Perubahan tetap kecil dan dekat dengan modul data yang memang bertanggung jawab.

## Performance Notes

Dataset hanya dibaca sekali per proses. Operasi mahal yang dipakai berulang dibuat menjadi cache:

- list material default: `_sorted_materials()`;
- pencarian multi-field: `_search_index()`;
- detail material: `_material_lookup()`;
- analytics: `analytics_summary()`.

Cache akan reset saat proses Streamlit restart. Untuk memakai file data lain tanpa mengubah kode, jalankan:

```bash
FLAVOR_DB_DATA_FILE=/path/to/materials.json.gz python3 -m streamlit run app.py
```

## Testing

Unit test berada di `tests/test_data_engine.py`. Test mencakup loader dataset utama, search, formatting, analytics, similar materials, dan hybrid reader untuk `.json` serta `.json.gz`.
