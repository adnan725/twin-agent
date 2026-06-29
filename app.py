from openai import OpenAI
from context import TWIN_SYSTEM_PROMPT
from tools import handle_tool_calls, record_user_details, unknown_user_details
from styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import gradio as gr
from agent import twin_agent
import asyncio
from agents import Agent, SQLiteSession, Runner, trace

load_dotenv(override=True)

MODEL_NAME = "gpt-5.4-mini"

openai = OpenAI()

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]

tools = [record_user_details, unknown_user_details]

# chat for non-agent
def chat(message, history):
    messages = system + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    return response.choices[0].message.content


# chat for agent
async def chat_agent(message, history):
    session = SQLiteSession("twin_chat")
    with trace("twin_agent"):
        result = await Runner.run(twin_agent, message, session=session)
    return result.final_output


async def main():
    result = await twin_agent()
    print(result)

if __name__ == "__main__":
    #asyncio.run(main())

    gr.ChatInterface(
        chat_agent,
        examples=EXAMPLES,
        title="Digital Twin",
        description="Talk to my AI twin about my career",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
