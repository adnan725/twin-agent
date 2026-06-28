import os
import json
from dotenv import load_dotenv
import requests

load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def send_pushover_message(message):
    if not pushover_user or not pushover_token:
        print("Pushover credentials are not set.")
        return

    payload = {
        "token": pushover_token,
        "user": pushover_user,
        "message": message
    }

    response = requests.post(pushover_url, data=payload)
    if response.status_code != 200:
        print("Failed to send Pushover message.")
    else:
        print("Pushover message sent successfully.")


def record_user_details(email, name='Name not provided', notes='notes not provided'):

    send_pushover_message(f"Recording interest from {name} with email {email} and notes {notes}")
    return 'OK'

def unknown_user_details(question):
    send_pushover_message(f"Recording {question} asked that I couldn't answer")
    return 'OK'


record_user_details_json = {
    "name": "record_user_details",
    "description": "Record user details and send a notification via Pushover.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of the user."
            },
            "name": {
                "type": "string",
                "description": "The name of the user.",
                "default": "Name not provided"
            },
            "notes": {
                "type": "string",
                "description": "Additional notes about the user.",
                "default": "notes not provided"
            }
        },
        "required": ["email"]
    }
}

unknown_user_details_json = {
    "name": "unknown_user_details",
    "description": "Record a question that the user asked that I couldn't answer and send a notification via Pushover.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that the user asked."
            }
        },
        "required": ["question"]
    }
}

tools = [
    { "type": "function", "function": record_user_details_json },
    { "type": "function", "function": unknown_user_details_json }
]

tool_map = {
    "record_user_details": record_user_details,
    "unknown_user_details": unknown_user_details
}

def handle_tool_call(tool_calls):
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.load(tool_call.arguments)
        print(f"Handling tool call for {tool_name} with arguments: {arguments}")
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else "unknown tool" + tool_name
        result.append(
            { "role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id }
        )
    return result