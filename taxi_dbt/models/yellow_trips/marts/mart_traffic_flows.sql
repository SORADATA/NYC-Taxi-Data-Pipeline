with trips as (
    select *
    from {{ ref('stg_trip') }}
),

zones as (
    select *
    from {{ ref('stg_taxi_zones') }}
),

traffic_flows as (
    select
        extract(hour from t.pickup_datetime) as pickup_hour,
        pul.borough as pickup_borough,
        pul.zone as pickup_zone,
        count(*) as total_departures,
        round(avg(t.trip_distance)::numeric, 2) as avg_distance,
        round(avg(t.total_amount)::numeric, 2) as avg_total_amount

    from trips t
    left join zones pul
        on t.pickup_location_id = pul.location_id

    group by
        extract(hour from t.pickup_datetime),
        pul.borough,
        pul.zone
)

select *
from traffic_flows
order by total_departures desc