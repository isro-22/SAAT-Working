# Flavor Chemical Database

Website database flavor/chemical materials berbasis Streamlit dengan database JSON lokal, search multi-field, dan detail material dalam 4 tab.

## Fitur

- Search multi-field: `name`, `synonyms`, `occurrence`, `organoleptic`, `FEMA`, `CAS`, `EINECS`, dan `JECFA`.
- Filter search field memakai checkbox satu baris dengan tombol `Apply Filters`, sehingga pilihan tidak langsung menjalankan pencarian sebelum diterapkan.
- Hasil pencarian memakai pagination 60 item per halaman; total hasil tetap dihitung penuh.
- Home page berupa list/table seperti referensi `konsep-1`.
- Detail page dengan 4 tab: `Identifier`, `Properties`, `Organoleptic`, dan `Insight`.
- Tab `Identifier` dan `Organoleptic` memakai layout list dua kolom seperti referensi konsep.
- Synonyms dirapikan menjadi daftar per baris.
- Descriptor organoleptic seperti `sweet`, `juicy`, `apple`, dan `woody` ditampilkan sebagai chip/link yang bisa diklik untuk mencari descriptor tersebut.
- Boilerplate `About FlavScents AInsights (Disclosure)` disembunyikan otomatis agar halaman detail tetap fokus pada data material.
- Halaman `Analytics` menampilkan overview database, coverage identifier, ranking descriptor/occurrence, duplicate CAS/name, CAS format issues, dan missing core identifiers.
- Detail material menampilkan `Similar Materials` berdasarkan overlap descriptor organoleptic, occurrence, dan kedekatan molecular weight.
- `My Shelf` menyimpan material pilihan selama sesi berjalan.
- Halaman `My Shelf` memiliki `Compare Materials` untuk membandingkan hingga 4 material tersimpan dalam satu tabel.
- Menu `Formulation Sheet` sudah disiapkan sebagai placeholder `Coming Soon / Under Construction` untuk fase berikutnya.
- UI Neo-Brutalism: border hitam tebal, shadow hitam tegas, aksen kuning, dan sudut tajam.
- Mode hybrid data reader: aplikasi otomatis membaca `materials_final.json` atau `materials_final.json.gz`.
- Data source bisa dioverride lewat environment variable `FLAVOR_DB_DATA_FILE`.
- Data engine memakai cache memory agar JSON besar, search index, sorted list, analytics, dan lookup detail tidak dihitung ulang di setiap rerun Streamlit.
- Optimasi mengikuti pendekatan `DietrichGebert/ponytail`: gunakan stdlib dulu, hilangkan duplikasi loader, dan tambah abstraksi hanya di boundary data yang memang sering dipakai.

## Struktur Folder

```text
.
├── app.py                         # Entry point Streamlit
├── data/
│   └── materials_final.json(.gz)  # Database material; JSON biasa atau gzip
├── docs/
│   └── assets/                    # Referensi desain dan screenshot
├── src/
│   └── flavor_db/
│       ├── app.py                 # UI Streamlit
│       └── data_engine.py         # Load, search, retrieval, mapping data
├── tests/
│   └── test_data_engine.py        # Unit test data engine
├── algorithm.md                   # Detail algoritma loader, search, lookup, analytics
├── architecture.md                # Boundary modul dan runtime architecture
├── requirements.txt
└── README.md
```

## Cara Menjalankan

Install dependency:

```bash
python3 -m pip install -r requirements.txt
```

Jalankan aplikasi:

```bash
python3 -m streamlit run app.py
```

Buka:

```text
http://localhost:8501
```

Opsional, gunakan file data lain:

```bash
FLAVOR_DB_DATA_FILE=/path/to/materials_final.json.gz python3 -m streamlit run app.py
```

## Testing

Jalankan unit test:

```bash
python3 -m unittest discover tests
```

Compile check:

```bash
python3 -m py_compile app.py src/flavor_db/app.py src/flavor_db/data_engine.py tests/test_data_engine.py
```

## Catatan Data

`materials_final.json` atau `materials_final.json.gz` berisi 26.610 material dan banyak field tambahan yang tidak selalu konsisten antar material. Field inti yang dipakai aplikasi:

- Identifier: `name`, `description`, `synonyms`, `cas`, `fema`, `einecs`, `jecfa_food_flavoring`, `jecfa_food_additive`, `dg_sante_food_flavourings`, `dg_sante_food_contact_materials`, `molecular_formula`.
- Properties: `molecular_weight`, `boiling_point`, `melting_point`, `soluble_in`, `flash_point`, `logp`, `appearance`.
- Organoleptic: `organoleptic_notes`, `odor`, `flavor`, `occurrence`.
- Insight: `ainsights_*`, regulation-related fields, safety-related fields.

Semua akses data melewati helper defensif agar nilai kosong, `N/A`, field hilang, list, atau dict tidak menyebabkan `KeyError`.

## Dokumentasi Teknis

- [algorithm.md](algorithm.md) menjelaskan algoritma hybrid loader, search scoring, lookup detail, similar materials, dan analytics.
- [architecture.md](architecture.md) menjelaskan flow runtime Streamlit, data boundary, cache, dan pendekatan `ponytail`.
