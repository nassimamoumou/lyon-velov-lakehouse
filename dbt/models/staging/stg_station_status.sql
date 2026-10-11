-- Nettoyage de l'état des stations : exclusion des points techniques, heure de Paris
select
    station_number,
    name                                         as station_name,
    address,
    latitude,
    longitude,
    status,
    bike_stands,
    available_bikes,
    available_bike_stands,
    last_update                                  as observed_at,
    (last_update at time zone 'Europe/Paris')    as observed_at_local,
    date_trunc('hour', last_update)              as weather_hour
from {{ source('raw', 'station_status') }}
-- "0-555 - ATELIER VÉLO'V" est l'atelier de réparation, pas une station ouverte au public
where name not like '0-%'
