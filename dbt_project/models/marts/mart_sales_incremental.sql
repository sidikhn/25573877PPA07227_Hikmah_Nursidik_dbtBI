{{
    config(
        materialized='incremental',
        unique_key='sale_id'
    )
}}

/*
  Mart 3: Model Penjualan Incremental (Bonus Point +3)
  Model ini menerapkan materialisasi incremental pada dbt.
  Pada initial run, model ini memuat seluruh data.
  Pada run berikutnya, model hanya memuat baris dengan sale_date
  lebih baru dibanding data yang sudah tersimpan sebelumnya.
*/

WITH staged AS (
    SELECT * FROM {{ ref('stg_sales') }}
)

SELECT
    sale_id,
    sale_date,
    product_id,
    product_name,
    city,
    quantity,
    unit_price,
    total_amount,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM staged

{% if is_incremental() %}
  WHERE sale_date > (SELECT MAX(sale_date) FROM {{ this }})
{% endif %}
