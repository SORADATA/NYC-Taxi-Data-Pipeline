WITH trip as (
    SELECT * 
    FROM {{ref('stg_trip')}}
),
trip_metrics as (
    SELECT
       tpep_dropoff_datetime,
       tpep_pickup_datetime,
       total_amount,
       fare_amount,
       trip_distance

       DATETIME_DIFF(
        tpep_dropoff_datetime,
        tpep_pickup_datetime,
        MINUTE
       ) AS duration_time

    FROM trip
),

trip_categories as (
    SELECT * 
        CASE
            WHEN tpep_dropoff_datetime IS NULL,
            OR tpep_pickup_datetime IS NULL
            THEN "MISSING_TIME"
            WHEN tpep_dropoff_datetime < tpep_pickup_datetime THEN "INVALID_TIME",
            WHEN duration_time > 3 THEN " LONG_TRIP",
            WHEN total_amount < 0 THEN "NEGATIVE_AMOUNT",
            WHEN trip_distance <= 0 AND  IS NOT NULL THEN "INVALID_DISTANCE"
            ELSE "NORMAL"
            END AS anomaly_category
    FROM trip_metrics
),
SELECT 
    anomaly_category,
    COUNT(*) as trip_count,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_trip

FROM trip_categories
GROUP BY anomaly_category
ORDER BY trip_count DESC;