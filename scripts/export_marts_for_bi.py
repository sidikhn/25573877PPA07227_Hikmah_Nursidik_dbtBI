"""
Script untuk mengekspor tabel hasil transformasi mart dari DuckDB
ke file CSV terkurasi agar mudah dihubungkan ke Power BI Desktop,
serta mencetak analisis kuantitatif kualitas data sebelum dan sesudah dbt.
"""

from pathlib import Path
import duckdb

def main():
    base_dir = Path(__file__).resolve().parents[1]
    db_path = base_dir / "data" / "warehouse.duckdb"
    export_dir = base_dir / "dashboard" / "data_export"
    export_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Menghubungkan ke DuckDB: {db_path}")
    con = duckdb.connect(str(db_path))

    # 1. Ekspor Mart Tables ke CSV
    marts = [
        ("mart_daily_sales", export_dir / "mart_daily_sales.csv"),
        ("mart_sales_by_city_product", export_dir / "mart_sales_by_city_product.csv"),
        ("mart_sales_incremental", export_dir / "mart_sales_incremental.csv"),
    ]

    print("\n--- Ekspor Model Mart untuk Power BI ---")
    for table_name, out_file in marts:
        con.execute(f"COPY (SELECT * FROM {table_name}) TO '{out_file.as_posix()}' (HEADER, DELIMITER ',');")
        count = con.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
        print(f"[+] Tabel '{table_name}' diekspor ke: {out_file.name} ({count} baris)")

    # 2. Analisis Kuantitatif Data Quality (Bab C Dokumentasi)
    raw_stats = con.execute("""
        SELECT
            COUNT(*) AS raw_total_rows,
            COUNT(DISTINCT sale_id) AS raw_unique_ids,
            COUNT(*) - COUNT(DISTINCT sale_id) AS raw_duplicates,
            SUM(CASE WHEN sale_id IS NULL THEN 1 ELSE 0 END) AS null_sale_id,
            SUM(CASE WHEN sale_date IS NULL THEN 1 ELSE 0 END) AS null_sale_date,
            SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END) AS null_quantity,
            SUM(CASE WHEN unit_price IS NULL THEN 1 ELSE 0 END) AS null_unit_price,
            SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) AS null_total_amount,
            SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END) AS null_city
        FROM raw.sales;
    """).fetchdf()

    staging_stats = con.execute("""
        SELECT
            COUNT(*) AS stg_total_rows,
            COUNT(DISTINCT sale_id) AS stg_unique_ids,
            COUNT(*) - COUNT(DISTINCT sale_id) AS stg_duplicates,
            SUM(CASE WHEN sale_id IS NULL THEN 1 ELSE 0 END) AS null_sale_id,
            SUM(CASE WHEN sale_date IS NULL THEN 1 ELSE 0 END) AS null_sale_date,
            SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END) AS null_quantity,
            SUM(CASE WHEN unit_price IS NULL THEN 1 ELSE 0 END) AS null_unit_price,
            SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) AS null_total_amount,
            SUM(CASE WHEN city IS NULL OR city = 'Unknown' THEN 1 ELSE 0 END) AS unknown_or_null_city
        FROM stg_sales;
    """).fetchdf()

    kpi_summary = con.execute("""
        SELECT
            SUM(total_revenue) AS total_revenue_all,
            SUM(total_orders) AS total_orders_all,
            SUM(total_units_sold) AS total_units_all,
            ROUND(AVG(avg_order_value), 2) AS overall_aov
        FROM mart_daily_sales;
    """).fetchdf()

    print("\n--- Analisis Kuantitatif Data Quality: RAW vs STAGING ---")
    print("Statistik Data RAW:")
    print(raw_stats.to_string())
    print("\nStatistik Data STAGING:")
    print(staging_stats.to_string())

    print("\n--- KPI Ringkasan untuk Power BI ---")
    print(kpi_summary.to_string())

    con.close()
    print("\n[OK] Ekspor dan analisis selesai.")

if __name__ == "__main__":
    main()
