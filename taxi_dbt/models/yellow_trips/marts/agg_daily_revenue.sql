/*
    Suivi Économique & Performance Globale :
*/

with trips as (
    select *
    from {{ ref('stg_trip') }}
),

daily_aggregation as (
    select
        cast(pickup_datetime as date) as trip_date,
        count(*) as total_trips,
        sum(passenger_count) as total_passengers,
        sum(trip_distance) as total_distance_miles,
        sum(fare_amount) as total_fare_amount,
        sum(tip_amount) as total_tip_amount,
        sum(total_amount) as total_revenue,
        avg(tip_percentage) as average_tip_percentage

    from trips
    group by cast(pickup_datetime as date)
)

select *
from daily_aggregation
order by trip_date