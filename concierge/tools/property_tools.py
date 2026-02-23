import os
import sqlite3
from typing import Optional, Dict, Any

from google.adk.tools.tool_context import ToolContext


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
)
DB_PATH = os.path.join(DATA_DIR, "properties.db")


def _normalize_property_name(property_name: str) -> str:
    """Normalize property name to the key used in data (e.g. 'Sunset Villa' -> 'sunset_villa')."""
    return property_name.strip().lower().replace(" ", "_")


def _row_to_property_dict(row: tuple) -> Dict[str, Any]:
    """Map a properties table row to the same dict shape as before (wifi and host nested)."""
    (
        id_,
        name,
        location,
        wifi_ssid,
        wifi_password,
        checkin,
        checkout,
        parking,
        house_rules,
        host_name,
        host_phone,
    ) = row
    return {
        "name": name,
        "location": location,
        "wifi": {"ssid": wifi_ssid, "password": wifi_password},
        "checkin": checkin,
        "checkout": checkout,
        "parking": parking,
        "house_rules": house_rules,
        "host": {"name": host_name, "phone": host_phone},
    }


def get_property_details(property_name: str) -> Optional[Dict[str, Any]]:
    """
    Look up property details by name or identifier.

    Args:
        property_name: The property name in any form (e.g. "Sunset Villa", "sunset villa",
            or "sunset_villa"). It is normalized by lowercasing and replacing spaces with underscores
            to match keys in the data source.

    Returns:
        A dict with keys: name, location, wifi (ssid, password), checkin, checkout,
        parking, house_rules, host (name, phone). Returns None if the property is not found
        or property_name is empty.
    """
    if not property_name:
        return None

    normalized = _normalize_property_name(property_name)
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            """
            SELECT id, name, location, wifi_ssid, wifi_password,
                   checkin, checkout, parking, house_rules, host_name, host_phone
            FROM properties
            WHERE id = ?
            """,
            (normalized,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    return _row_to_property_dict(row)


def set_guest_property(property_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Store the guest's current property in session state for cross-turn context.

    Call this when the guest indicates which property they are staying at (e.g. "I'm at Sunset Villa").
    The stored value is used as the default property when the guest does not specify one later.

    Args:
        property_name: The property name (e.g. "Sunset Villa" or "Downtown Loft").
        tool_context: ADK tool context; used to write session state (injected by the framework).

    Returns:
        A dict with status and current_property key on success, or error message if property is unknown.
    """
    details = get_property_details(property_name)
    if not details:
        return {
            "error": "Unknown property. Use 'Sunset Villa' or 'Downtown Loft'.",
            "status": "error",
        }
    normalized = _normalize_property_name(property_name)
    tool_context.state["current_property"] = normalized
    return {"status": "ok", "current_property": normalized}