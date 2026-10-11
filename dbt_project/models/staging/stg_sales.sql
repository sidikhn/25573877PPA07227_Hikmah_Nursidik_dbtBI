{{ config(materialized='view') }}

WITH source_data AS (
    SELECT
        sale_id,
        sale_date,
        product_id,
        product_name,
        quantity,
        unit_price,
        total_amount,
        city
    FROM {{ source('raw', 'sales') }}
    WHERE sale_id IS NOT NULL
      AND sale_date IS NOT NULL
      AND quantity IS NOT NULL
      AND unit_price IS NOT NULL
),

deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY sale_id 
            ORDER BY 
                (CASE WHEN product_name IS NOT NULL THEN 1 ELSE 0 END) +
                (CASE WHEN city IS NOT NULL THEN 1 ELSE 0 END) DESC
        ) AS row_num
    FROM source_data
),

cleaned AS (
    SELECT
        CAST(sale_id AS BIGINT) AS sale_id,
        TRY_CAST(sale_date AS DATE) AS sale_date,
        COALESCE(TRIM(product_id), 'P000') AS product_id,
        COALESCE(TRIM(product_name), 'Unknown Product') AS product_name,
        CAST(quantity AS INTEGER) AS quantity,
        CAST(unit_price AS DOUBLE) AS unit_price,
        -- Hitung ulang total_amount jika null atau tidak konsisten
        COALESCE(
            CAST(total_amount AS DOUBLE),
            CAST(quantity AS INTEGER) * CAST(unit_price AS DOUBLE)
        ) AS total_amount,
        COALESCE(NULLIF(TRIM(city), ''), 'Unknown') AS city
    FROM deduplicated
    WHERE row_num = 1
)

SELECT
    sale_id,
    sale_date,
    product_id,
    product_name,
    quantity,
    unit_price,
    total_amount,
    city
FROM cleaned
WHERE sale_date IS NOT NULL
  AND quantity > 0
  AND unit_price > 0
