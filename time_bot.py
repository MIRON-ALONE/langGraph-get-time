from langgraph.graph import StateGraph, END, MessagesState, START
from langgraph.prebuilt import ToolNode
from langchain.chat_models import init_chat_model
from langchain.tools import tool
import datetime
import os

# Tool definition
@tool
def get_current_time() -> dict:
    """Return the current UTC time in ISO‑8601 format."""
    return {"utc": datetime.datetime.utcnow().isoformat() + "Z"}

key = os.getenv("OPENAI_API_KEY") # <--- add openAI api key

tools = [get_current_time]
tool_node = ToolNode([get_current_time])

#Model init -->
model = init_chat_model("openai:gpt-4.1", openai_api_key=key)
model_with_tools = model.bind_tools([get_current_time])
print("-----> the model was initial <-----")

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

builder = StateGraph(MessagesState)
print("---> BUILDER WAS INITIAL <---")

# Define the two nodes we will cycle between
builder.add_node("call_model", call_model)
builder.add_node("tools", tool_node)

builder.add_edge(START, "call_model")
builder.add_conditional_edges("call_model", should_continue, ["tools", END])
builder.add_edge("tools", "call_model")

graph = builder.compile()
print("GRAPH WAS COMPILE")

graph.invoke({"messages": [{"role": "user", "content": "content"}]})

