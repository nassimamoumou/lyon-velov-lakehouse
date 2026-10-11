select
    weather_hour,
    temperature_c,
    precipitation_mm,
    wind_speed_kmh
from {{ source('raw', 'weather_hourly') }}
