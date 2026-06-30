from agents import Agent, trace, Runner, function_tool, ModelSettings
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import asyncio
import os
from tools import send_email_tool

load_dotenv(override=True)

MODEL_NAME = os.getenv("MODEL_NAME")

intro = """
You are a sales agent working for Nexora, 
a company that provides a SaaS tool for ensuring SOC2 compliance and 
preparing for audits, powered by AI.
You write emails.
"""

instructions1 = intro + "Your email style is professional, serious, with gravitas and credibility."
instructions2 = intro + "Your email style is witty, engaging, and humorous."
instructions3 = intro + "Your email style is concise, to the point, in the style of a busy senior executive."

message = "Write a cold sales email"


decision = """
You pick the best cold sales email from the given options. Send this email from Nexora to Adnan
Imagine you are a customer and pick the one you are most likely to respond to.
Do not give an explanation; reply with the selected email only.
"""

professional_agent = Agent(
    name="professional agent",
    instructions=instructions1,
    model=MODEL_NAME
)

witty_agent = Agent(
    name="Witty agent",
    instructions=instructions2,
    model=MODEL_NAME
)

exacutive_agent = Agent(
    name="exacutive agent",
    instructions=instructions3,
    model=MODEL_NAME
)

sales_picker = Agent(
    name='sales picker',
    instructions=decision,
    model=MODEL_NAME,
    tools=[send_email_tool],
    model_settings=ModelSettings(tool_choice="required")
)



async def main() -> str:
    #result = await Runner.run(professional_agent, "write sales email to Ayesha from Adnan")
    #print(result.final_output)

    with trace("parallel agents"):
        results = await asyncio.gather(
            Runner.run(professional_agent, message),
            Runner.run(witty_agent, message),
            Runner.run(exacutive_agent, message)
        )

    outputs = [ result.final_output for result in results ]

    emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

    best_email = Runner.run_streamed(sales_picker, emails)
    
    async for event in best_email.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())