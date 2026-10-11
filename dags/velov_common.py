"""Fonctions partagées par les DAG : connexion PostgreSQL, création des tables brutes, collectes."""
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import psycopg2
import requests
from psycopg2.extras import execute_values

PARIS = ZoneInfo("Europe/Paris")
LYON_LATITUDE, LYON_LONGITUDE = 45.7578, 4.8320

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
PUBLIC_HOLIDAYS_URL = "https://calendrier.api.gouv.fr/jours-feries/metropole.json"
SCHOOL_HOLIDAYS_URL = (
    "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "fr-en-calendrier-scolaire/records"
)

RAW_TABLES_SQL = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE IF NOT EXISTS raw.weather_hourly (
    weather_hour     TIMESTAMPTZ PRIMARY KEY,
    temperature_c    DOUBLE PRECISION,
    precipitation_mm DOUBLE PRECISION,
    wind_speed_kmh   DOUBLE PRECISION,
    ingested_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.public_holidays (
    holiday_date DATE PRIMARY KEY,
    holiday_name TEXT NOT NULL,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.school_holidays (
    description    TEXT        NOT NULL,
    population     TEXT        NOT NULL,
    start_date     TIMESTAMPTZ NOT NULL,
    end_date       TIMESTAMPTZ NOT NULL,
    annee_scolaire TEXT,
    zones          TEXT,
    ingested_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (description, population, start_date)
);
"""


def connect():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def ensure_raw_tables() -> None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(RAW_TABLES_SQL)


# ---------- Météo (Open-Meteo, sans clé d'API) ----------

def parse_weather(payload: dict) -> list[tuple]:
    hourly = payload["hourly"]
    rows = []
    for i, time_str in enumerate(hourly["time"]):
        hour = datetime.fromisoformat(time_str).replace(tzinfo=timezone.utc)
        rows.append((
            hour,
            hourly["temperature_2m"][i],
            hourly["precipitation"][i],
            hourly["wind_speed_10m"][i],
        ))
    return rows


def load_weather() -> int:
    ensure_raw_tables()
    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": LYON_LATITUDE,
            "longitude": LYON_LONGITUDE,
            "hourly": "temperature_2m,precipitation,wind_speed_10m",
            "past_days": 7,
            "forecast_days": 1,
            "timezone": "UTC",
        },
        timeout=30,
    )
    response.raise_for_status()
    rows = parse_weather(response.json())
    with connect() as conn, conn.cursor() as cur:
        execute_values(
            cur,
            """INSERT INTO raw.weather_hourly
                   (weather_hour, temperature_c, precipitation_mm, wind_speed_kmh)
               VALUES %s
               ON CONFLICT (weather_hour) DO UPDATE SET
                   temperature_c = EXCLUDED.temperature_c,
                   precipitation_mm = EXCLUDED.precipitation_mm,
                   wind_speed_kmh = EXCLUDED.wind_speed_kmh,
                   ingested_at = now()""",
            rows,
        )
    return len(rows)


# ---------- Jours fériés (calendrier.api.gouv.fr) ----------

def parse_public_holidays(payload: dict) -> list[tuple]:
    return [(datetime.strptime(day, "%Y-%m-%d").date(), name) for day, name in payload.items()]


def load_public_holidays() -> int:
    ensure_raw_tables()
    response = requests.get(PUBLIC_HOLIDAYS_URL, timeout=30)
    response.raise_for_status()
    rows = parse_public_holidays(response.json())
    with connect() as conn, conn.cursor() as cur:
        execute_values(
            cur,
            """INSERT INTO raw.public_holidays (holiday_date, holiday_name) VALUES %s
               ON CONFLICT (holiday_date) DO UPDATE SET holiday_name = EXCLUDED.holiday_name""",
            rows,
        )
    return len(rows)


# ---------- Vacances scolaires (data.education.gouv.fr, académie de Lyon) ----------

def parse_school_holidays(records: list[dict]) -> list[tuple]:
    rows = {}
    for r in records:
        key = (r["description"], r.get("population") or "-", r["start_date"])
        rows[key] = (
            r["description"],
            r.get("population") or "-",
            datetime.fromisoformat(r["start_date"]),
            datetime.fromisoformat(r["end_date"]),
            r.get("annee_scolaire"),
            r.get("zones"),
        )
    return list(rows.values())


def load_school_holidays(school_years: tuple[str, ...] = ("2025-2026", "2026-2027")) -> int:
    ensure_raw_tables()
    years = " or ".join(f'annee_scolaire="{y}"' for y in school_years)
    records, offset = [], 0
    while True:
        response = requests.get(
            SCHOOL_HOLIDAYS_URL,
            params={"where": f'location="Lyon" and ({years})', "limit": 100, "offset": offset},
            timeout=30,
        )
        response.raise_for_status()
        page = response.json().get("results", [])
        records.extend(page)
        if len(page) < 100:
            break
        offset += 100
    rows = parse_school_holidays(records)
    if rows:
        with connect() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                """INSERT INTO raw.school_holidays
                       (description, population, start_date, end_date, annee_scolaire, zones)
                   VALUES %s
                   ON CONFLICT (description, population, start_date) DO UPDATE SET
                       end_date = EXCLUDED.end_date""",
                rows,
            )
    return len(rows)
