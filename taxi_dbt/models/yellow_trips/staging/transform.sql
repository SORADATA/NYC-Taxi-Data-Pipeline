WITH source as (
    select * exclude (VendorId, RatecodeID)
    from {{ source('yellow_taxi_nyc', 'raw_yellow_data') }}
),
renamed as (
    select
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
transformed as (
    select * REPLACE (
        cast(passenger_count as bigint) as passenger_count,
        cast(distance_miles as float) as distance_miles,
        cast(fare_amount as float) as fare_amount
    ),
    case 
        when payment_type = 1 then 'Credit Card'
        when payment_type = 2 then 'Cash'
        else 'Other' 
    end as payment_method,
    
    case 
        when payment_type = 1 then tip_amount / NULLIF(fare_amount, 0) 
        else 0 
    end as tip_percentage

    from renamed
),
filtered as (
    select *
    from transformed
    where dropoff_at > pickup_at
      and distance_miles > 0
      and total_amount >= 0
      and pickup_at >= '2025-01-01'
      and pickup_at <  '2025-04-01'
),
final as (
    select * from filtered
)

select * from final