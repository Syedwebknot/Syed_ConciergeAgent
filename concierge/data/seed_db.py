"""
Seed the SQLite properties database from properties.json.
Run once after clone or when resetting data: python -m concierge.data.seed_db
"""

import json
import os
import sqlite3


DATA_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(DATA_DIR, "properties.json")
DB_PATH = os.path.join(DATA_DIR, "properties.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS properties (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    wifi_ssid TEXT NOT NULL,
    wifi_password TEXT NOT NULL,
    checkin TEXT NOT NULL,
    checkout TEXT NOT NULL,
    parking TEXT NOT NULL,
    house_rules TEXT NOT NULL,
    host_name TEXT NOT NULL,
    host_phone TEXT NOT NULL
);
"""


def seed() -> None:
    """Create or replace the SQLite DB and populate it from properties.json."""
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        properties = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            """
            INSERT OR REPLACE INTO properties (
                id, name, location, wifi_ssid, wifi_password,
                checkin, checkout, parking, house_rules, host_name, host_phone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    key,
                    p["name"],
                    p["location"],
                    p["wifi"]["ssid"],
                    p["wifi"]["password"],
                    p["checkin"],
                    p["checkout"],
                    p["parking"],
                    p["house_rules"],
                    p["host"]["name"],
                    p["host"]["phone"],
                )
                for key, p in properties.items()
            ],
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
    print(f"Seeded {DB_PATH} from {JSON_PATH}")
