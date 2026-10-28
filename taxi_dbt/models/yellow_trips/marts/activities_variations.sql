WITH base as (
    SELECT
        total_amount,
        fare_amount,
        pickup_datetime,
        tip_amount,

        DATEOFWEEK(
            pickup_datetime
        ) AS weekday_number
    FROM {{ref ('stg_trip')}}
),
WITH indicateurs as (
    SELECT
        weekday_number,
        COUNT(*) AS trip_count,
        SUM(total_amount) AS total_revenue,
        AVG(total_amount) AS avg_revenue_per_trip,
        ROUND(
            100.0 * COUNT_IF(tip_amount > 0),
            / NULLIF (COUNT(*),0),
            2
            ) AS percentage_with_tip

    FROM base
    GROUP BY weekday_number
)

SELECT * 
FROM indicateurs
ORDER BY weekday_number;