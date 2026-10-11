from datetime import timezone

from ingestion.fetch_velov import parse_station

SAMPLE = {
    "number": 10001,
    "contract_name": "lyon",
    "name": "10001 - EXEMPLE",
    "address": "Place Exemple",
    "position": {"lat": 45.76, "lng": 4.83},
    "status": "OPEN",
    "bike_stands": 20,
    "available_bikes": 7,
    "available_bike_stands": 13,
    "last_update": 1791700000000,
}


def test_parse_station_fields():
    row = parse_station(SAMPLE)
    assert row["station_number"] == 10001
    assert row["latitude"] == 45.76
    assert row["available_bikes"] + row["available_bike_stands"] == row["bike_stands"]


def test_last_update_is_utc_datetime():
    row = parse_station(SAMPLE)
    assert row["last_update"].tzinfo == timezone.utc
    assert row["last_update"].year == 2026
