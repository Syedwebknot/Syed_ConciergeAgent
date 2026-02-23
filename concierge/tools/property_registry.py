import os
import sqlite3
from typing import Optional


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
)
DB_PATH = os.path.join(DATA_DIR, "properties.db")


def get_all_properties() -> dict:
    """Return all properties from SQLite as a dict keyed by property id."""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT id, name, location, wifi_ssid, wifi_password,
                   checkin, checkout, parking, house_rules, host_name, host_phone
            FROM properties
            """
        ).fetchall()
    finally:
        conn.close()

    result = {}
    for row in rows:
        (id_, name, location, wifi_ssid, wifi_password, checkin, checkout,
         parking, house_rules, host_name, host_phone) = row
        result[id_] = {
            "name": name,
            "location": location,
            "wifi": {"ssid": wifi_ssid, "password": wifi_password},
            "checkin": checkin,
            "checkout": checkout,
            "parking": parking,
            "house_rules": house_rules,
            "host": {"name": host_name, "phone": host_phone},
        }
    return result


def resolve_property_from_text(text: str) -> Optional[str]:
    """
    Attempts to resolve a valid property key from user text.
    Returns normalized property key if found.
    """
    properties = get_all_properties()
    text_lower = text.lower()
    for key, value in properties.items():
        if value["name"].lower() in text_lower:
            return key
    return None