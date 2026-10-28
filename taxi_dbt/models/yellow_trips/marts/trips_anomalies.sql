
WITH trip_metrics AS (

    SELECT
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        fare_amount,
        total_amount,
        trip_distance,

        DATEDIFF(
            minute,
            tpep_pickup_datetime,
            tpep_dropoff_datetime
        ) AS duration_minutes

    FROM {{ ref('stg_trip') }}

),

trip_categories AS (

    SELECT
        *,
        CASE
            WHEN tpep_pickup_datetime IS NULL
              OR tpep_dropoff_datetime IS NULL
                THEN 'MISSING_TIME'

            WHEN duration_minutes < 0
                THEN 'INVALID_TIME'

            WHEN duration_minutes > 180
                THEN 'LONG_TRIP'

            WHEN total_amount < 0
                THEN 'NEGATIVE_AMOUNT'

            WHEN trip_distance IS NOT NULL
             AND trip_distance <= 0
                THEN 'INVALID_DISTANCE'

            ELSE 'NORMAL'
        END AS anomaly_category

    FROM trip_metrics

)

SELECT
    anomaly_category,
    COUNT(*) AS trip_count,

    ROUND(
        100.0 * COUNT(*)
        / NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS percentage_of_trips

FROM trip_categories

GROUP BY anomaly_category
ORDER BY trip_count DESC
