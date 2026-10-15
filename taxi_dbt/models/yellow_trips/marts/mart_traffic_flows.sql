with trips as (
    select * from {{ref('stg_trip')}}
),

zones as (
    select * from {{ref('stg_taxi_zones')}}
),

traffic_flows as (
    select
        extract(hour from pickup_datetime) as pickup_hour,
        pul.borough as pickup_borough,
        pul.zone as pickup_zone,
        count(*) as total_departures,
        round(avg(trip_distance), 2) as avg_distance,
        round(avg(total_amount), 2) as avg_total_amount

    from trips t
    left join zones pul
      on t.pickup_location_id = pul.location_id
    group by
        pickup_hour,
        pickup_borough,
        pickup_zone
)
select * from traffic_flows
order by total_departures desc