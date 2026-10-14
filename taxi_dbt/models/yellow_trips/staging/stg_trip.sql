with source as (
    select * from {{ source('yellow_taxi_nyc', 'raw_yellow_data') }}
),

renamed as (
    select
        -- Identifiants
        VendorID as vendor_id,
        PULocationID as pickup_location_id,
        DOLocationID as dropoff_location_id,

        -- Horodatages
        cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
        cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,

        -- Métriques de trajet
        cast(passenger_count as integer) as passenger_count,
        cast(trip_distance as double) as trip_distance,
        cast(RatecodeID as integer) as rate_code_id,

        -- Attributs de trajet
        store_and_fwd_flag,

        -- Informations financières
        cast(payment_type as integer) as payment_type,
        cast(fare_amount as double) as fare_amount,
        cast(extra as double) as extra,
        cast(mta_tax as double) as mta_tax,
        cast(tip_amount as double) as tip_amount,
        cast(tolls_amount as double) as tolls_amount,
        cast(improvement_surcharge as double) as improvement_surcharge,
        cast(total_amount as double) as total_amount,
        cast(congestion_surcharge as double) as congestion_surcharge,
        cast(Airport_fee as double) as airport_fee

    from source
),

transformed as (
    select
        *,

        -- Libellé du fournisseur
        case 
            when vendor_id = 1 then 'Creative Mobile Technologies, LLC'
            when vendor_id = 2 then 'Curb Mobility, LLC'
            when vendor_id = 6 then 'Myle Technologies Inc'
            when vendor_id = 7 then 'Helix'
            else 'Other_vendor'
        end as vendor_name,

        -- Libellé du code tarifaire (RatecodeID)
        case 
            when rate_code_id = 1 then 'Standard rate'
            when rate_code_id = 2 then 'JFK'
            when rate_code_id = 3 then 'Newark'
            when rate_code_id = 4 then 'Nassau or Westchester'
            when rate_code_id = 5 then 'Negotiated fare'
            when rate_code_id = 6 then 'Group ride'
            when rate_code_id = 99 then 'Null/unknown'
            else 'Other'
        end as rate_code_description,

        -- Libellé d'indicateur de stockage et retransmission
        case 
            when store_and_fwd_flag = 'Y' then 'Store and forward trip'
            when store_and_fwd_flag = 'N' then 'Not a store and forward trip'
            else 'Unknown'
        end as store_and_fwd_label,

        -- Libellé du type de paiement
        case 
            when payment_type = 1 then 'Credit Card'
            when payment_type = 2 then 'Cash'
            else 'Other' 
        end as payment_method,
        
        -- Calcul du pourcentage de pourboire
        case 
            when payment_type = 1 then tip_amount / NULLIF(fare_amount, 0) 
            else 0 
        end as tip_percentage

    from renamed
),

filtered as (
    select *
    from transformed
    where dropoff_datetime > pickup_datetime
      and trip_distance > 0
      and total_amount >= 0
      and pickup_datetime >= '2025-01-01'
      and pickup_datetime <  '2025-04-01'
),

final as (
    select * from filtered
)

select * from final