from agents import Agent
from dotenv import load_dotenv
from context import TWIN_SYSTEM_PROMPT
from tools import record_user_details, unknown_user_details

load_dotenv(override=True)

twin_agent = Agent(
    name="Digital Twin",
    instructions=TWIN_SYSTEM_PROMPT,
    model="gpt-5.4-mini",
    tools=[record_user_details, unknown_user_details],
)