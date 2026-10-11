-- Calendrier 2025-2027 enrichi des jours fériés et des vacances scolaires de Lyon
with days as (
    select generate_series('2025-01-01'::date, '2027-12-31'::date, interval '1 day')::date as date_day
)
select
    d.date_day,
    extract(year from d.date_day)::int                           as year,
    extract(month from d.date_day)::int                          as month,
    extract(isodow from d.date_day)::int                         as day_of_week,
    case extract(isodow from d.date_day)::int
        when 1 then 'lundi' when 2 then 'mardi' when 3 then 'mercredi' when 4 then 'jeudi'
        when 5 then 'vendredi' when 6 then 'samedi' else 'dimanche'
    end                                                          as day_name,
    extract(isodow from d.date_day) >= 6                         as is_weekend,
    ph.holiday_date is not null                                  as is_public_holiday,
    ph.holiday_name                                              as public_holiday_name,
    exists (
        select 1 from {{ ref('stg_school_holidays') }} sh
        where d.date_day >= sh.start_date and d.date_day < sh.end_date
    )                                                            as is_school_holiday
from days d
left join {{ ref('stg_public_holidays') }} ph on ph.holiday_date = d.date_day
