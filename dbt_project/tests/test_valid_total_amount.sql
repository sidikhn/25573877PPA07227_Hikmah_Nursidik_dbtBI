/*
  Singular Test: test_valid_total_amount.sql
  Identifikasi Masalah Kualitas Data:
  1. Ketidakkonsistenan perhitungan total_amount terhadap perkalian quantity * unit_price.
  2. Adanya nilai non-positif (kuantitas atau harga satuan <= 0).

  Ketentuan dbt Singular Test:
  Query harus mengembalikan 0 baris agar test berstatus PASS.
  Jika ditemukan anomali kalkulasi atau nilai non-positif, query akan mengembalikan baris tersebut (FAIL).
*/

SELECT
    sale_id,
    quantity,
    unit_price,
    total_amount,
    (quantity * unit_price) AS expected_total,
    ABS(total_amount - (quantity * unit_price)) AS discrepancy
FROM {{ ref('stg_sales') }}
WHERE ABS(total_amount - (quantity * unit_price)) > 0.01
   OR quantity <= 0
   OR unit_price <= 0
   OR total_amount <= 0
