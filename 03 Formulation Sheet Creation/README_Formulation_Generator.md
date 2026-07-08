# Formulation Sheet Automation

Dokumen ini menjelaskan struktur sistem **Formulation Sheet Automation** berdasarkan template Excel yang sedang digunakan. Tujuan sistem ini adalah membuat proses pembuatan **Laboratory Formulation Sheet & Lab Work Instruction** menjadi lebih sederhana: user hanya mengisi input utama, lalu sistem menghitung dan menghasilkan sheet formula sesuai template.

---

## 1. Tujuan Sistem

Sistem ini dibuat untuk mengotomatisasi pembuatan formulation sheet dengan input sederhana.

User cukup mengisi data seperti:

- Product information
- Product specification
- Phase metadata
- Item code
- Item name
- Dosage mg/stick
- Optional work instruction override

Kemudian sistem akan menghasilkan:

- Formula sheet sesuai template
- Ratio %
- Dosage KG/MC
- Material price
- Formulation price
- Total per phase
- Work instruction otomatis
- Format final siap dicetak atau diekspor

---

## 2. Struktur Workbook

Workbook saat ini menggunakan beberapa sheet utama.

| Sheet | Fungsi |
|---|---|
| `INPUT` | Tempat user mengisi data sederhana |
| `Formula` | Output formulation sheet yang akan di-generate |
| `BOL-SAAT List` | Master database material untuk lookup item |
| `SAAT 777 (ORI)` | Referensi template asli / layout acuan |
| `Sheet1` | Sheet tambahan, tidak wajib dipakai |

> Catatan: untuk hasil paling stabil, sheet `SAAT 777 (ORI)` sebaiknya dipertahankan sebagai referensi layout asli.

---

## 3. Struktur Sheet `INPUT`

Sheet `INPUT` adalah pusat input user. User tidak perlu mengedit langsung sheet `Formula`.

### 3.1 Product Information

Bagian ini berada di kiri atas sheet `INPUT`.

| Field | Contoh Isi | Keterangan |
|---|---|---|
| Product Name | `SAAT_777_SKT_KSL12_DP_ID_PHW_I` | Nama produk |
| Formula Code | `CS_K-CK-LCDT-04_R00/...` | Kode formulasi |
| Product Weight (mg/stick) | `720` atau `1300` | Berat produk per stick |
| Clove Weight (mg/stick) | `240` atau `433.333333` | Berat clove per stick |
| Stick per MC | `10000` | Jumlah stick per master case |
| Prepared By | Nama personel | Pembuat formula |
| Date | `07/07/2026` | Tanggal pembuatan |

---

### 3.2 Flavor Development Reference & Product Specification

Field ini perlu dimasukkan ke `INPUT` karena sebelumnya belum tersedia pada versi awal framework.

| Field | Keterangan |
|---|---|
| Standard Control | Standar pembanding produk |
| Flavor Standard Reference | Referensi flavor standard |
| Tobacco Blend Code | Kode blend tembakau |
| Formulation Code | Kode formulasi utama |
| Single Capsule | Informasi single capsule |
| Double Capsule (Tobacco End) | Informasi capsule sisi tobacco end |
| Double Capsule (Mouth End) | Informasi capsule sisi mouth end |
| Sensory Parameter | Parameter sensori |
| Impact | Catatan impact |
| Flavor Aroma | Catatan aroma |
| Irritation | Catatan irritation |
| Cooling | Catatan cooling |

### Mapping ke Sheet `Formula`

Header dokumen wajib dipertahankan sebagai berikut:

| Field | Label | Value |
|---|---|---|
| Document No | `P1` | `Q1 = BOL-ID-BOLL-SPEC-003` |
| Revision No | `P2` | `Q2 = 00` |
| Effective Date | `P3` | `Q3 = Date` |

| Input | Cell Output di `Formula` |
|---|---|
| Standard Control | `C10` |
| Flavor Standard Reference | `J10` |
| Tobacco Blend Code | `C12` |
| Sensory Parameter | `J12` |
| Formulation Code | `C13` |
| Impact | `J13` |
| Single Capsule | `C14` |
| Flavor Aroma | `J14` |
| Double Capsule (Tobacco End) | `C15` |
| Irritation | `J15` |
| Double Capsule (Mouth End) | `C16` |
| Cooling | `J16` |

---

### Approval Block

Approval block ditulis ulang otomatis setelah summary `Casing & Top Flavor`, sehingga posisinya mengikuti row dinamis.

| Kolom | Role | Isi |
|---|---|---|
| A:E | Prepared By | Position, Name dari input `Prepared By`, Date, Signature |
| F:L | Reviewed By | Position, Name, Date, Signature |
| M:Q | Approved By | Position, Name, Date, Signature |

---

### 3.3 Phase Metadata

Phase metadata berisi informasi level phase/blok seperti casing code, description, blend ratio, dan application.

| Field | Keterangan |
|---|---|
| Phase | Nama phase |
| NAV Item Code | Kode NAV untuk phase/premix |
| NAV Item Description | Deskripsi NAV phase/premix |
| Blend Ratio | Rasio blend |
| Application % | Persentase aplikasi |

Contoh phase metadata:

| Phase | NAV Item Code | NAV Item Description | Blend Ratio | Application % |
|---|---|---|---:|---:|
| Casing Rajangan | `GEN-CS-00000` | `CS_RAJANGAN_R00` | `38%` | `3.0780%` |
| Casing Krosok | `GEN-CS-00001` | `CS_KROSOK_R00` | `20%` | `2.0000%` |
| Top Flavor | `GEN-TF-00001` | `TF_R00` | `100%` | `0.5000%` |
| Casing Pre-Mix | `GEN-PM-00001` | `Casing Pre-Mix` |  |  |
| Casing Pre-Mix 2 | `GEN-PM-00002` | `Casing Pre-Mix 2` |  |  |
| Flavor Pre-Mix 1 | `GEN-PM-00002` | `Flavor Pre-Mix 1` |  |  |
| Flavor Pre-Mix 2 | `GEN-PM-00003` | `Flavor Pre-Mix 2` |  |  |
| Flavor Pre-Mix 3 | `GEN-PM-00004` | `Flavor Pre-Mix 3` |  |  |

Phase utama wajib:

- `Casing Rajangan`
- `Casing Krosok`
- `Top Flavor`

Premix optional dan jumlahnya dinamis:

- `Casing Pre-Mix`, `Casing Pre-Mix 2`, `Casing Pre-Mix 3`, dst.
- `Flavor Pre-Mix 1`, `Flavor Pre-Mix 2`, `Flavor Pre-Mix 3`, dst.

Skema relasi premix:

- Premix dibuat sebagai phase/blok sendiri.
- Jika premix dipakai di phase utama, masukkan NAV Item Code / NAV Item Description premix tersebut sebagai material row di `Casing Rajangan`, `Casing Krosok`, atau `Top Flavor`.
- Material pembentuk premix diisi di phase premix terkait.
- Dengan cara ini, Casing/Top Flavor hanya melihat premix sebagai satu item, sedangkan komposisi detailnya tetap ada di blok premix.

### Mapping Phase Metadata ke `Formula`

| Phase | NAV Item Code | NAV Item Description | Blend Ratio | Application % |
|---|---:|---:|---:|---:|
| Casing Rajangan | `E21` | `E22` | `E23` | `E24` |
| Casing Krosok | `E34` | `E35` | `E36` | `E37` |
| Top Flavor | `E47` | `E48` | `E49` | `E50` |
| Casing Pre-Mix | `E74` | `E75` | - | - |
| Flavor Pre-Mix 1 | `E90` | `E91` | - | - |
| Flavor Pre-Mix 2 | `E131` | `E132` | - | - |
| Casing/Flavor Pre-Mix tambahan | Dinamis | Dinamis | - | - |

---

### 3.4 Material Input Table

Tabel material dimulai dari baris input bahan. Kolom yang digunakan:

| Kolom | Field | Wajib | Keterangan |
|---|---|---:|---|
| A | Phase | Ya | Nama phase tujuan |
| B | Item Code | Ya | Kode bahan baku |
| C | Item Name | Ya / bisa lookup | Nama bahan baku |
| D | Input Mode | Ya | `mg/stick` atau `%` |
| E | Dosage mg/stick | Wajib jika mode `mg/stick` | Input dosage langsung |
| F | Ratio % | Wajib jika mode `%` | Ratio material |
| G | Addition Sequence | Opsional | Bisa manual atau otomatis |
| H | Temperature | Opsional | Default bisa `Ambient` |
| I | Agitation Rate | Opsional | Default bisa `500 RPM` |
| J | Mixing Duration | Opsional | Default tergantung logic |
| K | Work Instruction Override | Opsional | Jika diisi, sistem pakai ini |
| L | Process Role | Opsional | Carrier, Solid Dissolve, Final Homogenization, dll |
| M | Notes | Opsional | Catatan tambahan |

Di Streamlit, kolom bantu `Required Fields` menunjukkan field yang harus diisi berdasarkan `Input Mode`:

- `mg/stick` -> isi `Dosage mg/stick`
- `%` -> isi `Ratio %`; `Application %` diambil otomatis dari Phase Metadata phase tersebut

Gunakan tombol `Save Data / Validate Draft` sebelum generate untuk menyimpan draft di session dan melihat daftar field yang masih perlu dilengkapi.
Gunakan tombol `Save <Phase>` untuk menyimpan satu phase metadata, atau `Save All Phase Metadata` untuk menyimpan semua phase metadata sekaligus.

Untuk kolom proses (`Temperature`, `Agitation Rate`, `Mixing Duration`, dan `Work Instruction Override`), input cukup diisi sekali pada salah satu material dengan `Addition Sequence` yang sama. Saat generate, kolom proses di sheet `Formula` akan otomatis di-merge per grup `Addition Sequence`, sehingga output tampil seperti blok instruksi kerja.

Contoh input material:

| Phase | Item Code | Item Name | Input Mode | Dosage mg/stick | Ratio % |
|---|---|---|---|---:|---:|
| Casing Rajangan | `GEN-WA-00001` | `WATER` | `mg/stick` | `1.25000` |  |
| Casing Rajangan | `GEN-CHM-00015` | `INVERT SUGAR` | `%` |  | `38` |

Perhitungan mode `%`:

```text
Dosage mg/stick = Material Ratio % * Phase Application % * (Product Weight - Clove Weight)
```

Contoh:

```text
38% * 3.078% * (720 - 240) = 5.61427 mg/stick
```

Semua hasil `Dosage mg/stick` ditampilkan dengan 5 angka di belakang koma.

Contoh lama input material:

| Phase | Item Code | Item Name | Dosage mg/stick |
|---|---|---|---:|
| Casing Rajangan | `GEN-CHM-00015` | `INVERT SUGAR` | `2` |
| Casing Rajangan | `GEN-CHM-00016` | `SV-PROPYLENE GLYCOL...` | `2` |
| Casing Rajangan | `GEN-CHM-00004` | `SV-VEGETABLE GLYCERINE...` | `1` |
| Casing Rajangan | `GEN-FBL-00000` | `FBL_CK-04_R00` | `1.25` |
| Flavor Pre-Mix 3 | `GEN-WA-00001` | `WATER` | `1.00` |
| Flavor Pre-Mix 3 | `GEN-CHM-00015` | `INVERT SUGAR` | `2.00` |

> Format angka dosage menggunakan 5 desimal: `0.00000`, agar hasil mode `%` dan `mg/stick` konsisten.

---

## 4. Struktur Phase pada Template

Template original memiliki phase/blok utama berikut. Baris awal ini hanya titik awal layout; generator dapat menyembunyikan atau menambah baris material sesuai jumlah input.

| Phase | Judul Row Original | Data Row Original | Total Row Original | Baris Awal Template |
|---|---:|---:|---:|---:|
| Casing Rajangan | `20` | `26:30` | `31` | 5 baris |
| Casing Krosok | `33` | `39:43` | `44` | 5 baris |
| Top Flavor | `46` | `52:53` | `54` | 2 baris |
| Casing Pre-Mix | `73` | `77:86` | `87` | 10 baris |
| Flavor Pre-Mix 1 | `89` | `93:127` | `128` | 35 baris |
| Flavor Pre-Mix 2 | `130` | `134:142` | `143` | 9 baris |
| Casing/Flavor Pre-Mix tambahan | Dinamis | Dinamis | Dinamis | Clone dari template premix |

### Catatan Dynamic Row

Semua phase bersifat dinamis:

| Phase | Aturan |
|---|---|
| Phase utama | Wajib ada minimal satu material |
| Premix | Optional |
| Semua phase dengan data | Jumlah row output mengikuti jumlah material input |
| Premix kosong | Ditampilkan 3 row kosong sebagai area input/review |
| Jumlah material melebihi baris awal template | Generator menyisipkan row tambahan otomatis |
| Jumlah material kurang dari baris awal template | Generator menyembunyikan row kosong bawaan template agar merge template tetap stabil |
| Premix tambahan | Generator clone section premix dan menggeser layout berikutnya |

Python generator menyalin style baris material, menggeser section berikutnya saat overflow, menyembunyikan row kosong saat underflow, serta memperbarui referensi total dan Formulation Code berdasarkan posisi metadata terbaru.

---

## 5. Kolom Output pada Sheet `Formula`

Sheet `Formula` menggunakan kolom A sampai Q.

| Kolom | Field | Sumber |
|---|---|---|
| A | No | Auto numbering |
| B | Material NAV Item Code | Dari `INPUT` atau lookup |
| C:D | Material Name | Dari `INPUT` atau lookup |
| E | Physical Form / Physical State | Lookup dari `BOL-SAAT List` |
| F | CAS Number | Lookup dari `BOL-SAAT List` |
| G | Ratio (%) | Auto calculation |
| H | Dosage (mg/stick) | Dari `INPUT` |
| I | Material Price (USD/KG) | Lookup dari `BOL-SAAT List` |
| J | Formulation Price (USD/KG) | Auto calculation |
| K | Dosage (KG/MC) | Auto calculation |
| L | Density | Lookup / optional |
| M | Addition Sequence | Dari input atau auto |
| N | Temperature | Merge otomatis per `Addition Sequence` |
| O | Agitation Rate | Merge otomatis per `Addition Sequence` |
| P | Mixing Duration | Merge otomatis per `Addition Sequence` |
| Q | Work Instruction | Override atau auto-generate, merge otomatis per `Addition Sequence` |

---

## 6. Summary Casing & Top Flavor

Blok summary `Casing & Top Flavor` di bawah section `Top Flavor` selalu berisi 3 baris:

| Row Summary | Kolom B | Kolom C | Kolom D | Kolom G | Kolom H |
|---|---|---|---|---|---|
| 1 | Casing Rajangan NAV Item Description | Total Dosage Casing Rajangan `mg/stick` | Blend Ratio Casing Rajangan | Total Formulation Price Casing Rajangan `USD/KG` | 1,000 Sticks Price |
| 2 | Casing Krosok NAV Item Description | Total Dosage Casing Krosok `mg/stick` | Blend Ratio Casing Krosok | Total Formulation Price Casing Krosok `USD/KG` | 1,000 Sticks Price |
| 3 | Top Flavor Item Description | Total Dosage Top Flavor `mg/stick` | Blend Ratio Top Flavor | Total Formulation Price Top Flavor `USD/KG` | 1,000 Sticks Price |

Rumus `1,000 Sticks Price (USD)` per baris:

```excel
=G87*(C87/1000000)*1000
```

Nomor row mengikuti posisi dinamis aktual di workbook output.

---

## 7. Master Material: `BOL-SAAT List`

Sheet `BOL-SAAT List` berfungsi sebagai database material.

| Field Referensi | Kolom |
|---|---|
| Item Code | A |
| Item Name | E |
| Price USD/KG | G |
| CAS Number | H |
| Appearance / Physical State | I |

Lookup dapat dilakukan berdasarkan `Item Code` atau `Item Name`. Untuk sistem yang lebih stabil, disarankan menggunakan `Item Code` sebagai key utama.

---

## 8. Perhitungan Otomatis

### 8.1 Ratio %

Ratio dihitung berdasarkan total dosage dalam phase yang sama.

```text
Ratio (%) = Dosage Material / Total Dosage Phase
```

Contoh:

```excel
G26 = H26 / $H$31
```

### 8.2 Total Dosage

```text
Total Dosage Phase = SUM(Dosage semua material dalam phase)
```

Contoh:

```excel
H31 = SUM(H26:H30)
```

### 8.3 Formulation Price

```text
Formulation Price = Ratio * Material Price
```

Contoh:

```excel
J26 = G26 * I26
```

### 8.4 Dosage KG/MC

```text
Dosage KG/MC = Dosage mg/stick * Stick per MC / 1,000,000
```

Contoh:

```excel
K26 = H26 * $J$18 / 1000000
```

---

## 9. Work Instruction Logic

Work Instruction tidak cukup hanya dibedakan berdasarkan `Liquid` dan `Solid`.

Insight yang lebih tepat:

```text
Work Instruction = Phase + Addition Sequence + Physical State + Posisi Material + Process Role
```

### Rule sederhana yang bisa dipakai

| Kondisi | Work Instruction |
|---|---|
| Baris pertama phase dan terdapat solid | `Magnetic stirrer. Mix till all solids are dissolved.` |
| Baris pertama phase tanpa solid | `Magnetic stirrer. Start mixing base materials till uniform.` |
| Material solid | `Add gradually. Mix till completely dissolved.` |
| Material paste/extract/viscous | `Add gradually. Mix till fully dispersed and uniform.` |
| Baris terakhir phase | `Magnetic stirrer. Mix till homogeneous.` |
| User mengisi override | Pakai text dari `Work Instruction Override` |

Jika beberapa material memakai `Addition Sequence` yang sama, output `Addition Sequence`, `Temperature`, `Agitation Rate`, `Mixing Duration`, dan `Work Instruction` akan digabung vertikal. Nilai yang ditampilkan diambil dari input pertama yang terisi dalam grup tersebut; khusus `Work Instruction`, `Work Instruction Override` dari user diprioritaskan sebelum instruksi otomatis.

### Process Role yang disarankan

| Process Role | Fungsi |
|---|---|
| Carrier/Base | Pelarut atau base utama |
| Solid Dissolve | Bahan padat yang perlu dilarutkan |
| Liquid Addition | Penambahan bahan cair |
| Paste/Extract Dispersion | Dispersi paste, extract, viscous material |
| Final Homogenization | Tahap akhir homogenisasi |

---

## 10. Status Implementasi VBA Saat Ini

Beberapa versi framework VBA sudah dicoba.

| Versi | Tujuan | Status |
|---|---|---|
| v1 | Setup input dan generate dasar | Berjalan awal |
| v2 | Debug-safe sheet checking | Membantu deteksi missing sheet |
| v3 | Copy Formula sheet dari workbook referensi | Membantu memperbaiki missing `Formula` |
| v4 | Tambah phase metadata | Menambahkan casing/top flavor metadata |
| v5 | Full header input | Menambahkan flavor development dan product specification |
| v6 | Dynamic rows | Menyebabkan out of memory pada beberapa kondisi |
| v7 | Lite dynamic rows | Masih out of memory |
| v8 | Low memory no rebuild | Ada perbaikan compile, tetapi VBA tetap berisiko untuk dynamic format kompleks |

### Masalah yang ditemukan di VBA

- `Subscript out of range` ketika sheet `Formula` belum ada
- Format decimal dosage terlalu pendek sehingga nilai kecil tampil `0.00`
- Top Flavor original hanya punya 2 row sehingga terjadi capacity full
- Dynamic insert row menyebabkan out of memory
- Copy sheet dan merged cell menyebabkan workbook menjadi berat
- Compile error muncul pada pemanggilan `UsedRange` yang berdiri sendiri

---

## 11. Rekomendasi Arsitektur Lanjutan

Untuk kebutuhan jangka panjang, sistem lebih disarankan menggunakan:

```text
Python Web App / Streamlit + Excel Template Output
```

### Alur Sistem yang Direkomendasikan

```text
User buka halaman input
↓
Isi Product Info
↓
Isi Product Specification
↓
Isi Phase Metadata
↓
Isi Material Table
↓
Klik Generate
↓
Python membaca template Excel
↓
Python lookup master material
↓
Python menghitung ratio, price, dosage KG/MC
↓
Python generate Excel final sesuai template
↓
User download hasil .xlsx
```

### Kenapa Python lebih cocok?

| Kebutuhan | VBA | Python |
|---|---|---|
| Input form modern | Terbatas | Sangat bisa |
| Dynamic row | Rawan memory | Lebih aman |
| Template kompleks | Sensitif | Lebih stabil dengan kontrol style |
| Multi-user | Kurang cocok | Cocok |
| Error handling | Terbatas | Lebih rapi |
| Maintenance | Sulit jika makin kompleks | Lebih mudah |

---

## 12. Struktur Project Python Saat Ini

Project sudah dirapikan agar file kode, template, referensi, dan output tidak bercampur di root folder.

```text
03 Formulation Sheet Creation/
│
├── app.py
├── formulation_generator.py
├── requirements.txt
├── README_Formulation_Generator.md
│
├── templates/
│   └── Template_Generate.xlsm
│
├── references/
│   └── 02._SAAT_777.xlsx
│
├── outputs/
│   └── generated/
│       └── Generated_Formulation_Sheet_*.xlsx
│
├── assets/
│   └── logo.png
│
├── tests/
│   └── test_formulation_generator.py
│
└── .venv/
```

### Fungsi Folder

| Folder / File | Fungsi |
|---|---|
| `app.py` | Aplikasi Streamlit untuk input, preview, validasi, export model JSON/CSV, dan download hasil |
| `formulation_generator.py` | Engine kalkulasi, lookup master, validasi backend, dynamic premix row, blank input exporter, model export JSON/CSV, dan writer Excel |
| `assets/logo.png` | Logo yang dimasukkan ke workbook output `.xlsx` |
| `templates/` | Template macro Excel yang dipakai generator |
| `references/` | Workbook referensi/original untuk audit layout dan formula |
| `outputs/generated/` | Hasil generate `.xlsx` dari aplikasi |
| `tests/` | Unit test untuk generator |

### Menjalankan Streamlit

Aktifkan virtual environment lalu jalankan:

```bash
.venv/bin/streamlit run app.py
```

Atau langsung:

```bash
.venv/bin/python -m streamlit run app.py
```

### Library Python yang digunakan

```text
streamlit
pandas
openpyxl
```

### 12.1 Model Export

Untuk kebutuhan pengembangan berikutnya, data model formulasi sudah disiapkan dalam format JSON terstruktur yang bisa dipakai seperti tabel database.

Struktur export:

```json
{
  "schema_version": "1.0",
  "model_type": "formulation_product",
  "product": { "...": "..." },
  "phase_metadata": [
    { "phase": "Casing Rajangan", "nav_code": "...", "description": "...", "blend_ratio": 38, "application": 3.078 }
  ],
  "materials": [
    { "phase": "Casing Rajangan", "item_code": "...", "item_name": "...", "dosage_input_mode": "mg/stick", "dosage_mg_stick": 1.25 }
  ]
}
```

Manfaatnya:

- mudah disimpan per produk
- mudah di-import ulang untuk edit berikutnya
- mudah dipindahkan ke database, API, atau data warehouse
- menjaga Excel sebagai output akhir, bukan satu-satunya sumber data

CSV tersedia dalam bentuk bundle ZIP berisi tiga file:

- `product.csv`
- `phase_metadata.csv`
- `materials.csv`

Ini menjaga struktur data tetap normalisasi ringan, tanpa memaksa semua informasi masuk ke satu tabel datar.

### 12.2 Current Data Flow

Urutan data yang sekarang dipakai sistem:

1. User isi `INPUT` di Streamlit.
2. Data disimpan sebagai `current_form_data` dan `materials_df`.
3. Sistem validasi draft dan menyimpan snapshot session.
4. Model diekspor ke `JSON` atau `CSV bundle` bila diperlukan.
5. Jika valid, model yang sama dipakai untuk generate workbook `.xlsx`.

Prinsip penting untuk pengembangan berikutnya:

- `FormulationInput` adalah sumber kebenaran utama di layer Python.
- `phase_metadata` dan `materials` jangan di-hardcode di Excel saja.
- Output Excel adalah rendering final, bukan satu-satunya model data.
- Jika menambah field baru, update berurutan di `app.py`, `build_formulation_input_from_dict`, `export_formulation_model`, lalu test.
- Jika menambah phase baru, update struktur phase di template, runtime layout, dan validasi phase utama.

---

## 13. Rencana Pengembangan

### Tahap 1 — Stabilkan Excel Input

- Finalisasi struktur `INPUT`
- Validasi nama phase
- Validasi dosage numeric
- Format decimal minimal 6 digit
- Pastikan master material lengkap

### Tahap 2 — Python Generator

- Baca template Excel asli
- Baca input material
- Lookup master material
- Generate formula output
- Pertahankan format template
- Tambah dynamic rows premix secara aman

### Tahap 3 — Web App

- Form product info
- Form product specification
- Editable material table
- Upload/download Excel
- Validation message
- Export final formula

### Tahap 4 — Production

- Login user
- Formula history
- Versioning formula
- Approval flow
- Export PDF
- Database formula dan material
- Sinkronisasi model export JSON ke storage/database

---

## 14. Catatan Penting

1. Jangan menghapus sheet `SAAT 777 (ORI)` jika masih menggunakan referensi layout.
2. Jangan menulis manual di sheet `Formula`, gunakan `INPUT`.
3. Gunakan `Item Code` sebagai key lookup utama.
4. Gunakan format angka dosage minimal `0.000000`.
5. Untuk phase yang materialnya banyak, Python lebih aman dibanding VBA.
6. Jika tetap menggunakan VBA, hindari copy seluruh worksheet berulang kali.
7. Template sumber tetap `.xlsm`, tetapi hasil generate aplikasi disimpan sebagai `.xlsx`.

---

## 15. Ringkasan Keputusan

Berdasarkan kondisi saat ini:

```text
VBA cocok untuk prototype awal.
Python Web App lebih cocok untuk sistem final.
```

Rekomendasi final:

```text
Gunakan Python / Streamlit sebagai generator utama,
dan tetap gunakan Excel template sebagai output final.
```
