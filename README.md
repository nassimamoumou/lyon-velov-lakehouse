# Lyon Vélo'v Lakehouse

Plateforme de données qui collecte en continu la disponibilité des stations Vélo'v de Lyon, la croise avec la météo et le calendrier, et prédit les stations vides.

> Étape 1 sur 8 : collecte des données dans PostgreSQL.

## Architecture (étape 1)

API JCDecaux → script Python (toutes les 60 s) → PostgreSQL (`raw.station_status`)

## Prérequis

- Docker et Docker Compose
- Une clé d'API gratuite JCDecaux : https://developer.jcdecaux.com

## Installation

```bash
cp .env.example .env      # puis renseignez JCDECAUX_API_KEY et un mot de passe
make up                   # démarre PostgreSQL et la collecte
make logs                 # vérifie que les données arrivent
```

## Vérifier les données

```sql
SELECT count(*), max(last_update) FROM raw.station_status;
```

## Tests

```bash
pip install -r ingestion/requirements.txt pytest
make test
```

## Données

Données Vélo'v fournies par JCDecaux. Vérifiez et citez la licence d'utilisation des données avant toute publication.
