-- Les dates sont fournies en UTC : on les ramène au jour calendaire de Paris.
-- end_date correspond au jour de reprise des cours.
select distinct
    description                                           as holiday_name,
    (start_date at time zone 'Europe/Paris')::date        as start_date,
    (end_date at time zone 'Europe/Paris')::date          as end_date,
    annee_scolaire                                        as school_year
from {{ source('raw', 'school_holidays') }}
where population <> 'Enseignants'
