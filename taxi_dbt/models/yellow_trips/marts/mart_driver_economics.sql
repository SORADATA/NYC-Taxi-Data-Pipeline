with trips as (
    select *
    from {{ ref('stg_trip') }}
),

driver_economics as (
    select
        payment_method,
        count(*) as total_trips,

        round(avg(trip_distance)::numeric, 2)
            as avg_distance_miles,

        round(avg(fare_amount)::numeric, 2)
            as avg_fare_amount,

        round(avg(tip_amount)::numeric, 2)
            as avg_tip_amount,

        round((avg(tip_percentage) * 100)::numeric, 2)
            as avg_tip_percentage_rate,

        round(avg(tolls_amount)::numeric, 2)
            as avg_tolls_amount,

        round(avg(total_amount)::numeric, 2)
            as avg_total_revenue_per_trip,

        round(sum(total_amount)::numeric, 2)
            as cumulative_revenue

    from trips
    group by payment_method
)

select *
from driver_economics
order by total_trips desc