with source as (

    select * from {{ source('taxi', 'raw_trips') }}

),

renamed as (

    select
        VendorID                 as vendor_id,
        tpep_pickup_datetime     as pickup_at,
        tpep_dropoff_datetime    as dropoff_at,
        passenger_count,
        trip_distance            as distance_miles,
        PULocationID             as pickup_zone_id,
        DOLocationID             as dropoff_zone_id,
        payment_type,
        fare_amount,
        tip_amount,
        total_amount

    from source

),

filtered as (

    select *
    from renamed
    where dropoff_at > pickup_at
      and distance_miles > 0
      and total_amount >= 0
      and pickup_at >= '2024-01-01'
      and pickup_at <  '2024-04-01'

)

select * from filtered