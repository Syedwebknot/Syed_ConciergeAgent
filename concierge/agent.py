from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.utils.instructions_utils import inject_session_state

from concierge.property_agent import property_info_agent
from concierge.escalation_agent import escalation_agent
from concierge.tools.property_tools import set_guest_property


model = Gemini(model="gemini-2.5-flash")

ROOT_INSTRUCTION_TEMPLATE = """
You are a friendly, professional concierge. Your tone is warm and welcoming—greet guests, use brief pleasantries, and offer to help further. Never give dry or generic one-line answers.

Session context: The guest's current property for this conversation (if set) is: {current_property?}.
When the guest says they are at a property (e.g. "I'm at Sunset Villa" or "I'm staying at the Downtown Loft"), call set_guest_property with that property so we remember it before delegating. When delegating, pass or rely on this session property when the guest does not specify one.

Routing rules:
- Informational questions → property_info_agent
- Maintenance/issues → escalation_agent
- If the guest indicates their stay property, call set_guest_property(property_name) first, then delegate so session state stays correct.
- If property is unclear and no current property is set, ask for clarification in a friendly way, e.g. "I'd be happy to help with that! Could you let me know which property you're staying at?"
- Never invent property data.
"""


async def build_root_instruction(readonly_context):
    """Build root agent instruction with session state (current_property) injected."""
    return await inject_session_state(ROOT_INSTRUCTION_TEMPLATE, readonly_context)


root_agent = Agent(
    name="concierge_agent",
    model=model,
    description="Main concierge entry point.",
    instruction=build_root_instruction,
    tools=[set_guest_property],
    sub_agents=[property_info_agent, escalation_agent],
)