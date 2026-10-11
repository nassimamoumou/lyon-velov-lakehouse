-- Schéma de la couche brute (exécuté automatiquement au premier démarrage de PostgreSQL)
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.station_status (
    station_number        INTEGER      NOT NULL,
    contract_name         TEXT         NOT NULL,
    name                  TEXT,
    address               TEXT,
    latitude              DOUBLE PRECISION,
    longitude             DOUBLE PRECISION,
    status                TEXT,
    bike_stands           INTEGER,
    available_bikes       INTEGER,
    available_bike_stands INTEGER,
    last_update           TIMESTAMPTZ  NOT NULL,
    ingested_at           TIMESTAMPTZ  NOT NULL DEFAULT now(),
    payload               JSONB        NOT NULL,
    PRIMARY KEY (station_number, last_update)
);

CREATE INDEX IF NOT EXISTS idx_station_status_last_update
    ON raw.station_status (last_update);
