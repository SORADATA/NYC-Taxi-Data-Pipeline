WITH daily_ressources as (
    select
        total_amount,
        pickup_datetime,
        DATE(pickup_datetime) AS trip_date,
        SUM(total_amount) AS daily_revenue
        GROUP BY daily_revenue
    from {{ref('stg_trip')}}
),

classement AS (
    SELECT
        trip_date,
        daily_revenue,
        RANK() OVER (
            ORDER BY daily_revenue DESC
        ) AS rang
    FROM daily_ressources

)
SELECT * 
FROM classement
WHERE rang <= 10
ORDER BY rang
LIMIT 10;