# Proyek Transformasi Data dengan dbt & BI Dashboard

**Mata Kuliah:** Data Warehouse dan Business Intelligence  
**Departemen:** Ilmu Komputer dan Elektronika, Universitas Gadjah Mada  
**Pengampu:** Rifki Afina Putri, S.T., M.S., Ph.D.  
**Nama Mahasiswa:** Hikmah Nursidik  
**NIM:** 25/573877/PPA/07227

---

## 📌 Deskripsi Proyek

Proyek ini merupakan kelanjutan dari implementasi **Pipeline ETL Airflow** yang memproses data transaksi penjualan ritel. Dalam proyek ini:

1. Data mentah dari pipeline Airflow dimuat ke dalam database lokal **DuckDB** (`data/warehouse.duckdb`) pada skema `raw`.
2. Lapisan transformasi dirapikan dan dimodelkan menggunakan **dbt (data build tool)** dengan adapter `dbt-duckdb` mengikuti struktur arsitektur modern data stack: **Staging (View) $\rightarrow$ Marts (Table & Incremental)**.
3. Kualitas data dijaga menggunakan **26 dbt tests** (kombinasi _generic tests_ dan _custom singular test_).
4. Hasil pemodelan disajikan melalui **Power BI Dashboard interaktif** (KPI, Tren Penjualan, Analisis Regional, dan Fitur _Drill-Down_).

---

## 📁 Struktur Direktori Repository

```text
25573877PPA07227_Hikmah_Nursidik_dbtBI/
|-- dbt_project/
|   |-- models/
|   |   |-- staging/
|   |   |   |-- stg_sales.sql
|   |   |   `-- schema.yml
|   |   `-- marts/
|   |       |-- mart_daily_sales.sql
|   |       |-- mart_sales_by_city_product.sql
|   |       |-- mart_sales_incremental.sql
|   |       `-- schema.yml
|   |-- tests/
|   |   `-- test_valid_total_amount.sql
|   |-- dbt_project.yml
|   `-- profiles.yml
|-- data/
|   `-- warehouse.duckdb
|-- dashboard/
|   |-- data_export/
|   |   |-- mart_daily_sales.csv
|   |   |-- mart_sales_by_city_product.csv
|   |   `-- mart_sales_incremental.csv
|   |-- sales_performance_dashboard.pbix
|   `-- screenshots/
|-- docs/
|   |-- screenshots langkah langkah/
|   `-- Dokumentasi_25573877PPA07227.pdf
|-- scripts/
|   |-- load_raw_duckdb.py
|   `-- export_marts_for_bi.py
`-- README.md
```

---

## ⚙️ Persyaratan Sistem & Instalasi

1. **Python 3.10+** (diuji pada Python 3.11.5 di Windows 10/11)
2. **Power BI Desktop** (untuk membuka berkas `.pbix`)

### Langkah Setup Environment:

Buka PowerShell / Terminal di dalam direktori `25573877PPA07227_Hikmah_Nursidik_dbtBI/`:

```powershell
# 1. Buat dan aktifkan virtual environment (jika belum ada)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalasi dependensi
pip install duckdb dbt-duckdb pandas
```

---

## 🚀 Panduan Menjalankan Proyek

### 1. Ingestion Data Mentah ke DuckDB

Jalankan script untuk memuat data mentah dari CSV tugas Airflow ke `data/warehouse.duckdb`:

```powershell
python scripts/load_raw_duckdb.py
```

_Output: 315 baris data termuat ke skema `raw.sales`._

### 2. Menjalankan dbt (Run, Test, Docs)

Masuk ke direktori `dbt_project`:

```powershell
cd dbt_project

# A. Uji koneksi DuckDB
dbt debug --profiles-dir .

# B. Jalankan transformasi model
dbt run --profiles-dir .

# C. Jalankan pengujian kualitas data (26 tests)
dbt test --profiles-dir .

# D. Generate dokumentasi dan visualisasi Lineage Graph
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

### 3. Ekspor Data Mart untuk Power BI

Kembali ke root folder dan jalankan script ekspor:

```powershell
cd ..
python scripts/export_marts_for_bi.py
```

File CSV mart siap digunakan di folder `dashboard/data_export/`.

---

## 📊 Hasil Transformasi & Data Quality

### Ringkasan Pembersihan Data (Raw vs Staging)

| Metrik Kualitas Data       | Kondisi Awal (Raw Data) | Hasil Pembersihan (Staging) | Keterangan Solusi                                  |
| :------------------------- | :---------------------: | :-------------------------: | :------------------------------------------------- |
| **Total Record**           |        315 baris        |        **257 baris**        | Record valid tanpa duplikasi                       |
| **Record Duplikat**        |        15 baris         |         **0 baris**         | Dihapus via window function deduplication          |
| **Missing `sale_date`**    |        18 baris         |         **0 baris**         | Record tanggal kosong dieliminasi                  |
| **Missing `quantity`**     |        12 baris         |         **0 baris**         | Dieliminasi karena tidak dapat dikalkulasi         |
| **Missing `unit_price`**   |        15 baris         |         **0 baris**         | Dieliminasi                                        |
| **Missing `total_amount`** |        11 baris         |         **0 baris**         | Dihitung ulang via formula `quantity * unit_price` |
| **Missing `city`**         |        14 baris         |         **0 baris**         | Di-impute secara aman menjadi `'Unknown'`          |

### Ringkasan Eksekusi dbt Test

- **Total Test:** 26 Data Tests.
- **Hasil:** **26 PASS / 0 FAIL / 0 ERROR** (100% lolos uji integritas).
- **Custom Singular Test:** `test_valid_total_amount` memverifikasi kesesuaian matematika `total_amount == quantity * unit_price` dan memastikan nilai selalu positif.

---

## 📈 Desain BI Dashboard (Power BI Desktop)

Dashboard dirancang dengan mematuhi prinsip hierarki visual dan efisiensi _data-ink ratio_:

1. **Halaman 1 – Executive Sales Overview:**
   - **4 KPI Cards Utama:**
     - Total Revenue: **Rp 1,66 Miliar**
     - Total Transactions: **257 Pesanan**
     - Total Units Sold: **800 Unit**
     - Average Order Value (AOV): **Rp 6,23 Juta**
   - **Line Chart:** Tren omzet penjualan harian sepanjang tahun 2025.
   - **Bar Chart:** Peringkat omzet penjualan berdasarkan kota cabang.
   - **Interactive Slicers:** Filter rentang tanggal dan seleksi kota.

2. **Halaman 2 – Regional & Product Drill-Down (Fitur Bonus +4 Poin):**
   - **Hierarchical Drill-Down:** Eksplorasi performa dari tingkat Kota $\rightarrow$ Jenis Produk.
   - **Matrix Heatmap:** Kontribusi volume unit dan nilai transaksi per produk di tiap wilayah.

---

## 🏆 Fitur Nilai Tambah (Bonus Points Achieved)

- **Incremental Materialization (+3 Poin):** Model `mart_sales_incremental.sql` menerapkan pemrosesan inkremental menggunakan konfigurasi `is_incremental()` dan `unique_key='sale_id'`.
- **Multi-page & Drill-Down Dashboard (+4 Poin):** Dashboard Power BI dilengkapi dua halaman analisis komprehensif dengan navigasi interaktif dan fitur hierarki _drill-down_.
