import os
import requests
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, SQLiteSession
load_dotenv(override=True)
from context import TWIN_SYSTEM_PROMPT
from tools import record_user_details, unknown_user_details

twin_agent = Agent(
    name="Digital Twin",
    instructions=TWIN_SYSTEM_PROMPT,
    model="gpt-5.4-mini",
    tools=[record_user_details, unknown_user_details],
)