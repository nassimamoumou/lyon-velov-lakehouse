"""Collecte la disponibilité des stations Vélo'v et l'enregistre dans PostgreSQL.

Usage :
    python ingestion/fetch_velov.py          # boucle infinie, une collecte par intervalle
    python ingestion/fetch_velov.py --once   # une seule collecte (pratique pour tester)
"""
import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone

import psycopg
import requests
from dotenv import load_dotenv

API_URL = "https://api.jcdecaux.com/vls/v1/stations"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("velov")

INSERT_SQL = """
INSERT INTO raw.station_status (
    station_number, contract_name, name, address, latitude, longitude, status,
    bike_stands, available_bikes, available_bike_stands, last_update, payload
) VALUES (
    %(station_number)s, %(contract_name)s, %(name)s, %(address)s, %(latitude)s,
    %(longitude)s, %(status)s, %(bike_stands)s, %(available_bikes)s,
    %(available_bike_stands)s, %(last_update)s, %(payload)s
)
ON CONFLICT (station_number, last_update) DO NOTHING
"""


def fetch_stations(api_key: str, contract: str, retries: int = 3) -> list[dict]:
    """Appelle l'API JCDecaux, avec quelques nouvelles tentatives en cas d'erreur réseau."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                API_URL, params={"contract": contract, "apiKey": api_key}, timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            log.warning("Tentative %s/%s échouée : %s", attempt, retries, error)
            time.sleep(5 * attempt)
    raise RuntimeError("API JCDecaux injoignable après plusieurs tentatives")


def parse_station(raw: dict) -> dict:
    """Transforme un enregistrement brut de l'API en ligne prête à insérer."""
    position = raw.get("position") or {}
    return {
        "station_number": raw["number"],
        "contract_name": raw["contract_name"],
        "name": raw.get("name"),
        "address": raw.get("address"),
        "latitude": position.get("lat"),
        "longitude": position.get("lng"),
        "status": raw.get("status"),
        "bike_stands": raw.get("bike_stands"),
        "available_bikes": raw.get("available_bikes"),
        "available_bike_stands": raw.get("available_bike_stands"),
        # last_update est fourni en millisecondes depuis 1970
        "last_update": datetime.fromtimestamp(raw["last_update"] / 1000, tz=timezone.utc),
        "payload": json.dumps(raw),
    }


def save(rows: list[dict], conninfo: str) -> int:
    """Insère les lignes ; les doublons (même station, même horodatage) sont ignorés."""
    with psycopg.connect(conninfo) as conn, conn.cursor() as cur:
        cur.executemany(INSERT_SQL, rows)
        return cur.rowcount


def run_once(api_key: str, contract: str, conninfo: str) -> None:
    stations = fetch_stations(api_key, contract)
    rows = [parse_station(s) for s in stations if s.get("last_update")]
    inserted = save(rows, conninfo)
    log.info("%s stations reçues, %s nouvelles lignes insérées", len(stations), inserted)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="une seule collecte")
    args = parser.parse_args()

    api_key = os.environ["JCDECAUX_API_KEY"]
    contract = os.getenv("JCDECAUX_CONTRACT", "lyon")
    interval = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    conninfo = (
        f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.environ['POSTGRES_DB']} "
        f"user={os.environ['POSTGRES_USER']} "
        f"password={os.environ['POSTGRES_PASSWORD']}"
    )

    while True:
        try:
            run_once(api_key, contract, conninfo)
        except Exception:  # on journalise et on continue : le service ne doit pas s'arrêter
            log.exception("Échec de la collecte")
        if args.once:
            break
        time.sleep(interval)


if __name__ == "__main__":
    main()
