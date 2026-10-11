select
    weather_hour,
    temperature_c,
    precipitation_mm,
    wind_speed_kmh,
    precipitation_mm >= 0.2 as is_rainy
from {{ ref('stg_weather') }}
