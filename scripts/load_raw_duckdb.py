"""
Script untuk memuat dataset raw dari output/input Airflow ke DuckDB lokal.
Dataset dimuat ke dalam schema 'raw' dengan nama tabel 'sales'.

Database target: data/warehouse.duckdb
"""

from pathlib import Path
import duckdb

def main():
    base_dir = Path(__file__).resolve().parents[1]
    db_path = base_dir / "data" / "warehouse.duckdb"
    
    # Path ke file data/raw/sales.csv dari proyek Airflow
    source_csv = base_dir.parent / "data" / "raw" / "sales.csv"
    if not source_csv.exists():
        # Fallback jika dijalankan dari konteks berbeda
        source_csv = Path(r"D:\S2-UGM\Data Warehouse\25573877PPA07227_Hikmah Nursidik_AirflowETL\code\airflow_tugas_25573877PPA07227\data\raw\sales.csv")

    print(f"[*] Sumber CSV: {source_csv}")
    print(f"[*] Target DuckDB: {db_path}")

    # Buat direktori data jika belum ada
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Koneksi ke DuckDB
    con = duckdb.connect(str(db_path))

    # Buat schema raw
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    # Load data dari CSV ke raw.sales
    # DuckDB bisa langsung membaca CSV dan menginferensikan skema
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.sales AS
        SELECT * FROM read_csv_auto('{source_csv.as_posix()}', header=True);
    """)

    # Verifikasi data yang masuk
    total_rows = con.execute("SELECT COUNT(*) FROM raw.sales;").fetchone()[0]
    unique_ids = con.execute("SELECT COUNT(DISTINCT sale_id) FROM raw.sales;").fetchone()[0]
    sample_rows = con.execute("SELECT * FROM raw.sales LIMIT 5;").fetchdf()

    print("\n[+] Berhasil memuat data ke DuckDB!")
    print(f"[+] Total Baris di raw.sales: {total_rows}")
    print(f"[+] Total Unique sale_id: {unique_ids}")
    print("\n--- Preview 5 Baris Pertama ---")
    print(sample_rows)

    # Cek statistik null dan anomali
    null_counts = con.execute("""
        SELECT
            COUNT(*) - COUNT(sale_id) AS null_sale_id,
            COUNT(*) - COUNT(sale_date) AS null_sale_date,
            COUNT(*) - COUNT(product_id) AS null_product_id,
            COUNT(*) - COUNT(product_name) AS null_product_name,
            COUNT(*) - COUNT(quantity) AS null_quantity,
            COUNT(*) - COUNT(unit_price) AS null_unit_price,
            COUNT(*) - COUNT(total_amount) AS null_total_amount,
            COUNT(*) - COUNT(city) AS null_city
        FROM raw.sales;
    """).fetchdf()
    print("\n--- Jumlah Null per Kolom (Raw Data Kualitas Awal) ---")
    print(null_counts)

    con.close()
    print("\n[OK] Koneksi database ditutup. File warehouse.duckdb siap digunakan oleh dbt.")

if __name__ == "__main__":
    main()
