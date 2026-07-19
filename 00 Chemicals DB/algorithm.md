# Algorithm

## Tujuan

Data engine dibuat untuk membaca database material besar sekali saja, lalu melayani pencarian dan detail material dari cache in-memory selama proses Streamlit berjalan.

## Hybrid JSON Loader

1. `resolve_material_data_file()` mencari data dari `FLAVOR_DB_DATA_FILE` jika environment variable diisi.
2. Jika tidak ada override, loader memilih `data/materials_final.json`.
3. Jika file JSON biasa tidak ada, loader otomatis memakai `data/materials_final.json.gz`.
4. `read_json_records()` memakai satu jalur validasi untuk dua format tersebut:
   - `.json` dibaca dengan `open()`.
   - `.json.gz` dibaca dengan `gzip.open()`.
   - Isi harus berupa list.
   - Item non-dict diabaikan agar data kotor tidak menjatuhkan aplikasi.

## Search

1. `load_materials()` membaca data dan dicache dengan `lru_cache(maxsize=1)`.
2. `_search_index()` membuat teks lower-case per grup field, lalu menyimpannya di cache.
3. `search_materials()` hanya memeriksa field yang dipilih user.
4. Skor hasil mengutamakan:
   - name exact match,
   - name prefix match,
   - jumlah kemunculan query pada field terpilih.
5. Hasil diurutkan dari skor tertinggi, lalu nama material.

## Detail Lookup

`_material_lookup()` membangun map dari `material_key`, `cas`, dan `name` ke object material. Ini membuat `get_material()` menjadi lookup O(1), bukan scan O(n) di setiap pembukaan halaman detail.

## Similar Materials

1. Descriptor diambil dari `organoleptic_notes`, `odor`, dan `flavor`.
2. Occurrence dipecah dari nilai pipe-delimited.
3. Candidate diberi skor dari overlap descriptor, overlap occurrence, dan kedekatan molecular weight.
4. Hasil dibatasi sesuai parameter `limit`.

## Analytics

`analytics_summary()` berjalan di atas data yang sudah dicache dan menghitung coverage field, descriptor populer, occurrence populer, duplicate CAS/name, format CAS yang tidak umum, dan material yang kehilangan identifier inti.
