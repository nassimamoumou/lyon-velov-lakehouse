import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dags"))

from velov_common import parse_public_holidays, parse_school_holidays, parse_weather  # noqa: E402


def test_parse_weather_is_utc_and_complete():
    payload = {"hourly": {
        "time": ["2026-10-11T13:00", "2026-10-11T14:00"],
        "temperature_2m": [14.2, 14.8],
        "precipitation": [0.0, 0.4],
        "wind_speed_10m": [9.0, 11.5],
    }}
    rows = parse_weather(payload)
    assert len(rows) == 2
    assert rows[1][0].utcoffset().total_seconds() == 0
    assert rows[1][2] == 0.4


def test_parse_public_holidays():
    rows = parse_public_holidays({"2026-11-01": "Toussaint"})
    assert rows[0][0].isoformat() == "2026-11-01"
    assert rows[0][1] == "Toussaint"


def test_parse_school_holidays_deduplicates():
    record = {
        "description": "Vacances de la Toussaint", "population": "-",
        "start_date": "2026-10-16T22:00:00+00:00", "end_date": "2026-11-01T23:00:00+00:00",
        "annee_scolaire": "2026-2027", "zones": "Zone A",
    }
    assert len(parse_school_holidays([record, record])) == 1
