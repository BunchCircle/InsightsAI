import operator
from typing import Sequence, TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from backend.core.data_models import InputData
from typing import Dict
import json
import pandas as pd
import numpy as np
from datetime import datetime, date


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'freq'):  # pandas Period objects
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        elif isinstance(obj, pd.Series):
            return obj.astype(str).tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.astype(str).to_dict()
        elif hasattr(obj, 'variable_name') and hasattr(obj, 'data_path') and hasattr(obj, 'data_description'):
            # Handle InputData objects
            return {
                'variable_name': obj.variable_name,
                'data_path': obj.data_path,
                'data_description': obj.data_description
            }
        elif hasattr(obj, 'content') and hasattr(obj, 'type'):
            # Handle LangChain message objects
            return {
                'content': obj.content,
                'type': obj.type,
                'additional_kwargs': getattr(obj, 'additional_kwargs', {})
            }
        return super().default(obj)


def serialize_state(state_dict):
    """Serialize state dictionary to ensure JSON compatibility"""
    try:
        json.dumps(state_dict, cls=CustomJSONEncoder)
        return state_dict
    except (TypeError, ValueError) as e:
        # If serialization fails, create a cleaned version
        cleaned_state = {}
        for key, value in state_dict.items():
            try:
                if isinstance(value, dict):
                    cleaned_state[key] = serialize_state(value)
                elif key == "input_data":
                    # Preserve InputData objects as they are needed for processing
                    cleaned_state[key] = value
                elif key == "messages":
                    # Preserve messages list as LangGraph handles it internally
                    cleaned_state[key] = value
                else:
                    json.dumps(value, cls=CustomJSONEncoder)
                    cleaned_state[key] = value
            except (TypeError, ValueError):
                if key in ["input_data", "messages"]:
                    # Preserve these key objects even if they can't be serialized
                    cleaned_state[key] = value
                else:
                    cleaned_state[key] = str(value)
        return cleaned_state


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    input_data: Annotated[List[InputData], operator.add]
    intermediate_outputs: Annotated[List[dict], operator.add]
    current_variables: dict
    output_image_paths: Annotated[List[str], operator.add]

from pydantic import BaseModel

class AgentStateModel(BaseModel):
    messages: List[dict]
    input_data: List[dict]
    intermediate_outputs: List[dict]
    current_variables: dict
    output_image_paths: List[str]
