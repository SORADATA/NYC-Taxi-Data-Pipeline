/*
     Gestion des Flux de Circulation : 
     - Identifie les corridors de transport saturés pour orienter la gestion des voies réservées aux Taxis/VTC.
*/

with trips as (
    select * from {{ref('stg_trip')}}
),

zones as (
    select * from {{ref('stg_taxi_zones')}}
),

routes as (
    select
        t.pickup_location_id,
        pul.borough as pickup_borough,
        pul.zone as pickup_zone,

        t.dropoff_location_id,
        dol.borough as dropoff_borough,
        dol.zone as dropoff_zone,

        count(*) as total_trips,
        round(avg(t.trip_distance), 2) as avg_distance_miles,
        round(avg(t.total_amount), 2) as avg_total_amount

    from trips t
    left join zones pul
      on t.pickup_location_id = pul.location_id
    left join zones dol
       on t.dropoff_location_id = dol.location_id
    group by 1, 2, 3, 4, 5, 6
)

select * from routes
order by total_trips desc