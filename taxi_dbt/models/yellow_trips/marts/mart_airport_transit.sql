/*
    Impact des Transports Aéroports (JFK, LaGuardia, Newark) : 
    Analyse spécifique de la desserte des aéroports pour ajuster la taxe de congestion et les frais d'accès.

*/

with trips as (
    select * from {{ ref('stg_trip') }}
),

zones as (
    select * from {{ ref('stg_taxi_zones') }}
),

airport_trips as (
    select
        t.vendor_id,
        t.vendor_name,
        t.pickup_datetime,
        t.dropoff_datetime,
        pul.zone as pickup_zone,
        dol.zone as dropoff_zone,
        t.trip_distance,
        t.fare_amount,
        t.airport_fee,
        t.total_amount,
        t.payment_method,
        case 
            when pul.zone ilike '%jfk%' or dol.zone ilike '%jfk%' then 'JFK Airport'
            when pul.zone ilike '%laguardia%' or dol.zone ilike '%laguardia%' then 'LaGuardia Airport'
            when pul.zone ilike '%newark%' or dol.zone ilike '%newark%' then 'Newark Airport'
            else 'Other Airport'
        end as target_airport
    from trips t
    left join zones pul on t.pickup_location_id = pul.location_id
    left join zones dol on t.dropoff_location_id = dol.location_id
    where pul.zone ilike '%jfk%' or dol.zone ilike '%jfk%'
       or pul.zone ilike '%laguardia%' or dol.zone ilike '%laguardia%'
       or pul.zone ilike '%newark%' or dol.zone ilike '%newark%'
       or pul.zone ilike '%airport%' or dol.zone ilike '%airport%'
)

select * from airport_trips