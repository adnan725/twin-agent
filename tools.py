import os
import json
import requests
from dotenv import load_dotenv
from agents import function_tool

load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def send_pushover_message(message):
    requests.post(
        pushover_url,
        data={
            "token": pushover_token,
            "user": pushover_user,
            "message": message,
        },
    )

@function_tool
def record_user_details(email: str, name: str = 'Name not provided', notes: str = 'notes not provided') -> str:
    """Use this tool to record that a user is interested in being in touch and provided an email address"""

    send_pushover_message(f"Recording interest from {name} with email {email} and notes {notes}")
    return 'OK'

@function_tool
def unknown_user_details(question: str) -> str:
    """Use this tool to record any question that couldn't be answered as you didn't know the answer"""

    send_pushover_message(f"Recording {question} asked that I couldn't answer")
    return 'OK'


# json schema for the tools
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {
                "type": "string",
                "description": "Any additional info about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

tools = [
    { "type": "function", "function": record_user_details_json },
    { "type": "function", "function": record_unknown_question_json }
]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": unknown_user_details
}

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Handling tool call for {tool_name} with arguments: {arguments}")
        tool = tool_map.get(tool_name)
        output = tool(**arguments) if tool else "unknown tool" + tool_name
        results.append(
            { "role": "tool", "content": json.dumps(output), "tool_call_id": tool_call.id }
        )
    return results