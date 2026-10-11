# Lyon Vélo'v Lakehouse

Plateforme de données qui collecte en continu la disponibilité des stations Vélo'v de Lyon, la croise avec la météo et le calendrier, et prédit les stations vides.

> Étape 2 sur 8 : orchestration Airflow et modélisation dbt.

## Architecture actuelle

- **Collecte temps réel** : un service Python interroge l'API JCDecaux toutes les 60 s et enregistre chaque changement d'état dans `raw.station_status`.
- **Collectes batch (Airflow)** : météo horaire (Open-Meteo), jours fériés et vacances scolaires de l'académie de Lyon.
- **Modélisation (dbt)** : schéma en étoile dans le schéma `marts`.

| Table | Contenu |
| --- | --- |
| `fct_station_status` | Une ligne par changement d'état d'une station (incrémentale) |
| `dim_station` | Référentiel des stations |
| `dim_date` | Calendrier, week-ends, jours fériés, vacances scolaires |
| `dim_weather` | Météo horaire |

Chaque heure, le DAG `velov_hourly` charge la météo puis lance `dbt build`, qui construit les tables et exécute 26 tests de qualité.

## Installation

Prérequis : Docker Desktop et une clé d'API gratuite [JCDecaux](https://developer.jcdecaux.com).

```bash
cp .env.example .env      # renseignez la clé d'API et les mots de passe
docker compose up -d --build
```

- Airflow : http://localhost:8080 (utilisateur `admin`, mot de passe `AIRFLOW_ADMIN_PASSWORD`)
- PostgreSQL : `localhost:5433`

## Exemple de requête

```sql
-- Part des stations vides par heure de la journée
select hour_local, round(avg(is_empty::int) * 100, 1) as pct_mesures_vides
from marts.fct_station_status
group by hour_local
order by hour_local;
```

## Choix techniques

- Seuls les changements d'état sont stockés (clé `station_number, last_update`), ce qui divise le volume par trois environ.
- La table de faits est incrémentale : chaque exécution ne retraite que les 3 dernières heures.
- Les horodatages de l'API sont en UTC et convertis à l'heure de Paris dans dbt.
- dbt est installé dans un environnement Python séparé d'Airflow pour éviter les conflits de dépendances.

## Données

Données Vélo'v fournies par JCDecaux, météo par Open-Meteo, calendrier par calendrier.api.gouv.fr et data.education.gouv.fr. Vérifiez et citez la licence de chaque source avant toute publication.
