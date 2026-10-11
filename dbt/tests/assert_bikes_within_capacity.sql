-- Signale les mesures où les vélos disponibles dépassent la capacité de la station
{{ config(severity='warn') }}
select *
from {{ ref('fct_station_status') }}
where available_bikes < 0
   or available_bikes > bike_stands
