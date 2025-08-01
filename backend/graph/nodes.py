from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from backend.graph.state import AgentState, serialize_state
import json
from typing import Literal
from backend.graph.tools import complete_python_task
# ToolExecutor and ToolInvocation are no longer needed
# Remove tool_executor and call_tools
import os
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4",  # or "gpt-3.5-turbo" if you prefer
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

tools = [complete_python_task]

model = llm.bind_tools(tools)

with open(os.path.join(os.path.dirname(__file__), "../prompts/main_prompt.md"), "r") as file:
    prompt = file.read()

chat_template = ChatPromptTemplate.from_messages([
    ("system", prompt),
    ("placeholder", "{messages}"),
])
model = chat_template | model

def create_data_summary(state: AgentState) -> str:
    summary = ""
    variables = []
    for d in state["input_data"]:
        # Handle both InputData objects and dictionaries (from serialization)
        if hasattr(d, 'variable_name'):
            # InputData object
            variable_name = d.variable_name
            description = d.data_description
        elif isinstance(d, dict) and 'variable_name' in d:
            # Dictionary from serialized InputData
            variable_name = d['variable_name']
            description = d.get('data_description', '')
        else:
            # Fallback for unexpected types
            variable_name = str(d)
            description = ''
        
        variables.append(variable_name)
        summary += f"\n\nVariable: {variable_name}\n"
        summary += f"Description: {description}"
    
    current_variables = state.get("current_variables") or {}
    remaining_variables = [v for v in current_variables if v not in variables]
    for v in remaining_variables:
        summary += f"\n\nVariable: {v}"
    return summary

def route_to_tools(
    state: AgentState,
) -> Literal["tools", "__end__"]:
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route back to the agent.
    """
    # Ensure messages is a list (in case it was serialized as a string)
    if isinstance(state.get("messages"), str):
        state["messages"] = []
    elif not isinstance(state.get("messages"), list):
        state["messages"] = []

    if messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"

def call_model(state: AgentState):
    # Ensure messages is a list (in case it was serialized as a string)
    if isinstance(state.get("messages"), str):
        state["messages"] = []
    elif not isinstance(state.get("messages"), list):
        state["messages"] = []

    current_data_template  = """The following data is available:\n{data_summary}"""
    current_data_message = HumanMessage(content=current_data_template.format(data_summary=create_data_summary(state)))
    state["messages"] = [current_data_message] + state["messages"]

    llm_outputs = model.invoke(state)
    print("llm_outputs: ", llm_outputs)

    return {"messages": [llm_outputs], "intermediate_outputs": [current_data_message.content]}

