with source as (
    select *
    from {{ ref('taxi_zone_lookup') }}
),

renamed as (
    select
        cast("LOCATIONID" as integer) as location_id,
        cast("BOROUGH" as varchar) as borough,
        cast("ZONE" as varchar) as zone,
        cast("SERVICE_ZONE" as varchar) as service_zone
    from source
)

select *
from renamed