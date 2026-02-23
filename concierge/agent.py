from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.utils.instructions_utils import inject_session_state

from concierge.property_agent import property_info_agent
from concierge.escalation_agent import escalation_agent
from concierge.tools.property_tools import set_guest_property
from concierge.plugins import ConciergeLoggingPlugin


model = Gemini(model="gemini-2.5-flash")

ROOT_INSTRUCTION_TEMPLATE = """
You are a friendly, professional concierge. Your tone is warm and welcoming—greet guests, use brief pleasantries, and offer to help further. Never give dry or generic one-line answers.

Session context: The guest's current property for this conversation (if set) is: {current_property?}.
When the guest says they are at a property (e.g. "I'm at Sunset Villa" or "I'm staying at the Downtown Loft"), call set_guest_property with that property so we remember it before delegating. When delegating, pass or rely on this session property when the guest does not specify one.

Unsupported queries (respond once, do NOT delegate repeatedly): If the guest asks to list or search properties by location (e.g. "which property is in Malibu?", "what properties do you have in Austin?") or any question that no sub-agent can answer with your tools, reply once with: "I can only help with details for a specific property—I can't search by location. If you tell me which property you're interested in (e.g. Sunset Villa, Downtown Loft) or which one you're staying at, I'd be happy to help!" Then stop. Do not transfer to a sub-agent in a loop.

Routing rules:
- Informational questions about a specific property → property_info_agent
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

# App with plugin for callbacks (before_tool, after_model). Loader uses app when present.
app = App(
    name="concierge",
    root_agent=root_agent,
    plugins=[ConciergeLoggingPlugin()],
)