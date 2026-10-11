select
    holiday_date,
    holiday_name
from {{ source('raw', 'public_holidays') }}
