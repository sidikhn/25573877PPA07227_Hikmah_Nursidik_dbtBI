{{ config(materialized='table') }}

/*
  Mart 2: Kinerja Penjualan Regional & Produk
  Model ini mengagregasi omzet, volume produk, dan jumlah transaksi
  berdasarkan kombinasi kota cabang dan jenis produk.
*/

WITH sales AS (
    SELECT * FROM {{ ref('stg_sales') }}
)

SELECT
    city,
    product_id,
    product_name,
    COUNT(DISTINCT sale_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(unit_price), 2) AS avg_unit_price,
    ROUND(AVG(total_amount), 2) AS avg_revenue_per_order
FROM sales
GROUP BY
    city,
    product_id,
    product_name
ORDER BY
    city ASC,
    total_revenue DESC
