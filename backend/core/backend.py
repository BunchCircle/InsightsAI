from langchain_core.messages import HumanMessage
from typing import List
from dataclasses import dataclass
from langgraph.graph import StateGraph
from backend.graph.state import AgentState, serialize_state
from backend.graph.nodes import call_model, route_to_tools, tools
from langgraph.prebuilt import ToolNode
from backend.core.data_models import InputData, User
import sqlite3
from passlib.hash import bcrypt

class PythonChatbot:
    def __init__(self):
        super().__init__()
        self.reset_chat()
        self.graph = self.create_graph()
        
    def create_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node('agent', call_model)
        workflow.add_node('tools', ToolNode(tools))

        workflow.add_conditional_edges('agent', route_to_tools)

        workflow.add_edge('tools', 'agent')
        workflow.set_entry_point('agent')
        return workflow.compile()
    
    def user_sent_message(self, user_query, input_data: List[InputData]):
        starting_image_paths_set = set(sum(self.output_image_paths.values(), []))
        input_state = {
            "messages": self.chat_history + [HumanMessage(content=user_query)],
            "output_image_paths": list(starting_image_paths_set),
            "input_data": input_data,
        }

        # Don't serialize the entire state - let LangGraph handle it
        # Only serialize specific parts if needed
        result = self.graph.invoke(input_state, {"recursion_limit": 25})
        self.chat_history = result["messages"]
        new_image_paths = set(result["output_image_paths"]) - starting_image_paths_set
        self.output_image_paths[len(self.chat_history) - 1] = list(new_image_paths)
        if "intermediate_outputs" in result:
            self.intermediate_outputs.extend(result["intermediate_outputs"])

    def reset_chat(self):
        self.chat_history = []
        self.intermediate_outputs = []
        self.output_image_paths = {}

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_user(username: str, password: str) -> bool:
    password_hash = bcrypt.hash(password)
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> bool:
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user and bcrypt.verify(password, user['password_hash']):
        return True
    return False

def get_user_by_username(username: str):
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user_row:
        return User(id=user_row['id'], username=user_row['username'], password_hash=user_row['password_hash'])
    return None
