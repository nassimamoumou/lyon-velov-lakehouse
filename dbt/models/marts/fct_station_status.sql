-- Table de faits : une ligne par changement d'état d'une station.
-- Incrémentale : à chaque exécution, on ne retraite que les 3 dernières heures.
{{
    config(
        materialized='incremental',
        unique_key='status_id',
        incremental_strategy='delete+insert',
        post_hook="create index if not exists fct_station_status_station_time_idx on {{ this }} (station_number, observed_at)"
    )
}}

select
    s.station_number || '-' || extract(epoch from s.observed_at)::bigint      as status_id,
    s.station_number,
    s.observed_at,
    s.observed_at_local,
    s.observed_at_local::date                                                 as date_day,
    extract(hour from s.observed_at_local)::int                               as hour_local,
    s.weather_hour,
    s.status,
    s.bike_stands,
    s.available_bikes,
    s.available_bike_stands,
    case when s.bike_stands > 0
         then round(s.available_bikes::numeric / s.bike_stands, 3) end        as occupancy_rate,
    s.available_bikes = 0                                                     as is_empty,
    s.available_bike_stands = 0                                               as is_full
from {{ ref('stg_station_status') }} s
{% if is_incremental() %}
where s.observed_at > (select max(observed_at) - interval '3 hours' from {{ this }})
{% endif %}
