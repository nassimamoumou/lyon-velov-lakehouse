-- Une ligne par station, avec ses attributs les plus récents
with ranked as (
    select
        *,
        row_number() over (partition by station_number order by observed_at desc) as rn,
        min(observed_at) over (partition by station_number)                        as first_seen_at
    from {{ ref('stg_station_status') }}
)
select
    station_number,
    station_name,
    address,
    latitude,
    longitude,
    bike_stands as capacity,
    first_seen_at
from ranked
where rn = 1
