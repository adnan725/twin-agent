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

description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."

task = """
Follow these steps:

1. Generate Drafts: Use each of the three sales_email_writer tools to generate different email drafts.
Just instruct each to write a sales email; no further details are needed.
Do not proceed until all three drafts are ready, one from each tool.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use your tool to send the best email (and only the best email) to the user. Only send 1 email.

4. You must also add this link in the email body for the user to ask more information and make this link
clickable where label is More Info with link behing it http://127.0.0.1:5000/follow-up
"""

instructions = """
You are a Sales Manager at Nexora. Your goal is to find the single best cold sales email using the sales_writer tools.
"""

professional_agent = Agent(
    name="professional agent",
    instructions=instructions1,
    model=MODEL_NAME
)

# above agent as tool
professional_agent_tool = professional_agent.as_tool(
    tool_name='professional_sales_emails_writer',
    tool_description=description
)

witty_agent = Agent(
    name="Witty agent",
    instructions=instructions2,
    model=MODEL_NAME
)

# above agent as tool
witty_agent_tool = witty_agent.as_tool(
    tool_name='witty_sales_emails_writer',
    tool_description=description
)

exacutive_agent = Agent(
    name="exacutive agent",
    instructions=instructions3,
    model=MODEL_NAME
)

# above agent as tool
exacutive_agent_tool = exacutive_agent.as_tool(
    tool_name='exacutive_sales_emails_writer',
    tool_description=description
)

tools = [professional_agent_tool, witty_agent_tool, exacutive_agent_tool, send_email_tool]

sales_picker = Agent(
    name='sales picker',
    instructions=decision,
    model=MODEL_NAME,
    tools=[send_email_tool],
    model_settings=ModelSettings(tool_choice="required")
)

sales_manager = Agent(
    name='Sales manager',
    instructions=instructions,
    tools=tools,
    model=MODEL_NAME,
    #model_settings=ModelSettings(tool_choice="required")
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


async def main_2() -> str:
    result = await Runner.run(sales_manager, task)
    return result.final_output

if __name__ == "__main__":
    #asyncio.run(main())
    asyncio.run(main_2())