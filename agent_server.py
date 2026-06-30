import requests
from flask import Flask
from agents import Agent, Runner
import asyncio
from tools import send_email_tool
import os

MODEL_NAME = os.getenv("MODEL_NAME")

instructions="You are a follow up agent who is asked to provide additional enformations about Nexora. How Nexora help increase the business activities"

app = Flask(__name__)

follow_up_agent = Agent(
    name="Follow up",
    instructions=instructions,
    model=MODEL_NAME
)



@app.route('/follow-up')
def follow_up():
    

    return 'Thanks! You will shortly recieve an Email with more information'

if __name__ == "__main__":
    app.run(debug=True)