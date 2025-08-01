from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_core.messages import AIMessage
from typing import Tuple
import sys
from io import StringIO
import os
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import pandas as pd
import sklearn
import json
from datetime import datetime, date
import numpy as np

repl = PythonREPL()
persistent_vars = {}

# --- Custom JSON Encoder ---
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'freq'):
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
        return super().default(obj)

def serialize_variable(var):
    try:
        if hasattr(var, 'freq') and hasattr(var, 'year'):
            return str(var)
        if isinstance(var, pd.Series):
            if var.dtype == 'object':
                return var.astype(str)
            return var
        if isinstance(var, pd.DataFrame):
            for col in var.columns:
                if var[col].dtype == 'object':
                    var[col] = var[col].astype(str)
            return var
        json.dumps(var, cls=CustomJSONEncoder)
        return var
    except (TypeError, ValueError):
        return str(var)

def clean_persistent_vars(vars_dict):
    cleaned = {}
    for key, value in vars_dict.items():
        if key not in globals():
            try:
                cleaned[key] = serialize_variable(value)
            except Exception:
                cleaned[key] = str(value)
    return cleaned

# --- HTML chart export block ---
plotly_html_saving_code = """
import uuid
import plotly
import os
from backend.core.chart_cleanup import record_chart_creation, cleanup_old_charts, cleanup_orphaned_files

os.makedirs("images/plotly_figures/html", exist_ok=True)

# Run cleanup before generating new charts
cleanup_old_charts()
cleanup_orphaned_files()

output_image_paths = []

for figure in plotly_figures:
    html_filename = f"{uuid.uuid4()}.html"
    filepath = os.path.join("images/plotly_figures/html", html_filename)
    plotly.offline.plot(figure, filename=filepath, auto_open=False)
    record_chart_creation(html_filename)
    output_image_paths.append(html_filename)
"""

# --- MAIN TOOL FUNCTION ---
@tool
def complete_python_task(
    graph_state: dict,
    thought: str,
    python_code: str
) -> Tuple[str, dict]:
    """
    Executes Python code for data analysis and visualization using pandas, sklearn, and plotly.
    Returns the standard output and any generated charts.
    """
    current_variables = graph_state.get("current_variables") or {}

    for input_dataset in graph_state["input_data"]:
        if hasattr(input_dataset, 'variable_name'):
            variable_name = input_dataset.variable_name
            data_path = input_dataset.data_path
        elif isinstance(input_dataset, dict) and 'variable_name' in input_dataset:
            variable_name = input_dataset['variable_name']
            data_path = input_dataset['data_path']
        else:
            continue

        if variable_name not in current_variables:
            print(f"Loading data from path: {data_path}")
            current_variables[variable_name] = pd.read_csv(data_path)

    os.makedirs("images/plotly_figures/html", exist_ok=True)
    current_files = set(os.listdir("images/plotly_figures/html"))

    try:
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        exec_globals = globals().copy()
        exec_globals.update(persistent_vars)
        exec_globals.update(current_variables)
        exec_globals["plotly_figures"] = []

        exec(python_code, exec_globals)

        new_persistent_vars = {k: v for k, v in exec_globals.items() if k not in globals()}
        cleaned_vars = clean_persistent_vars(new_persistent_vars)
        persistent_vars.update(cleaned_vars)

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        updated_state = {
            "intermediate_outputs": [{"thought": thought, "code": python_code, "output": output}],
            "current_variables": cleaned_vars
        }

        # Save charts to HTML
        if exec_globals.get("plotly_figures"):
            print(f"Found {len(exec_globals['plotly_figures'])} charts to save")
            exec(plotly_html_saving_code, exec_globals)
            html_paths = exec_globals.get("output_image_paths", [])
            print(f"Saved {len(html_paths)} HTML files: {html_paths}")
            if html_paths:
                updated_state["output_image_paths"] = html_paths
            persistent_vars["plotly_figures"] = []
        else:
            print("No plotly_figures found in exec_globals")

        return output, updated_state

    except Exception as e:
        return str(e), {
            "intermediate_outputs": [{
                "thought": thought,
                "code": python_code,
                "output": str(e)
            }]
        }
