import uuid
import asyncio
from datetime import datetime
from typing import Any, Dict

from concierge.tools.property_tools import get_property_details


async def create_support_ticket(property_name: str, issue_description: str) -> Dict[str, Any]:
    """
    Create a maintenance/support ticket for the given property (long-running operation).

    Simulates an async ticket creation: runs for a few seconds then returns a ticket id
    and structured details so the agent can confirm the request and provide host contact.

    Args:
        property_name: The property the issue relates to (e.g. "Sunset Villa", "Downtown Loft").
        issue_description: Description of the issue or request from the guest.

    Returns:
        A dict with: ticket_id (str), property (str), issue (str), status ("created"),
        created_at (ISO datetime string), and host_contact (dict with name, phone) for the
        property so the agent can always provide emergency/host contact in the response.
    """
    await asyncio.sleep(3)

    ticket_id = str(uuid.uuid4())[:8]
    details = get_property_details(property_name)
    host_contact: Dict[str, Any] = {}
    if details and "host" in details:
        host_contact = {
            "name": details["host"].get("name", ""),
            "phone": details["host"].get("phone", ""),
        }

    return {
        "ticket_id": ticket_id,
        "property": property_name,
        "issue": issue_description,
        "status": "created",
        "created_at": datetime.utcnow().isoformat(),
        "host_contact": host_contact,
    }