{{ config(materialized='table') }}

/*
  Mart 1: Ringkasan Kinerja Penjualan Harian
  Model ini mengagregasi data transaksi per tanggal untuk memantau
  tren omzet, volume pesanan, dan rata-rata nilai transaksi harian.
*/

WITH sales AS (
    SELECT * FROM {{ ref('stg_sales') }}
)

SELECT
    sale_date,
    COUNT(DISTINCT sale_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS avg_order_value,
    MIN(total_amount) AS min_order_value,
    MAX(total_amount) AS max_order_value
FROM sales
GROUP BY sale_date
ORDER BY sale_date ASC
