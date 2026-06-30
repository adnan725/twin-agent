import requests
from flask import Flask
from agents import Agent, Runner
import asyncio
from tools import send_email_tool
import os

MODEL_NAME = os.getenv("MODEL_NAME")

instructions="""
You are a follow up agent who is asked to provide additional enformations about Nexora. How Nexora help increase the business activities
You right email professionally with information in bullet points that is useful for Nexora customer
"""

task = """
You are asked to provide more information about Nexora. This information includes how Nexora help business grow
through reliable strategies. You will write an email to the user using send_email_tool
"""

description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."

app = Flask(__name__)

follow_up_agent = Agent(
    name="Follow up",
    instructions=instructions,
    model=MODEL_NAME
)

# above agent as tool
follow_up_agent_tool = follow_up_agent.as_tool(
    tool_name="follow_up_agent",
    tool_description=description
)

follow_up_manager = Agent(
    name="follow up manager",
    instructions="You will use all the tools to generate email and then send the result to user using email send tool",
    model=MODEL_NAME,
    tools=[follow_up_agent_tool, send_email_tool]
)

async def main():
    result = await Runner.run(follow_up_manager, task)
    print(result.final_output)    


@app.route('/follow-up')
def follow_up():
    asyncio.run(main())
    return 'Thanks! You will shortly recieve an Email with more information'

if __name__ == "__main__":
    app.run(debug=True)