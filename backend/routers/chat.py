from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import sqlite3
import pandas as pd
from backend.graph.tools import complete_python_task
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_human_response(question: str, analysis_result: str, charts: list, df: pd.DataFrame) -> str:
    # Prepare context for GPT
    columns_info = list(df.columns)
    sample_data = df.head(5).to_dict()
    chart_info = [f"Chart {i+1}: {chart}" for i, chart in enumerate(charts)]
    
    prompt = f"""Please provide a detailed, conversational response based on the following data analysis:

Context:
Dataset Columns: {columns_info}
Sample Data: {sample_data}

User Question: {question}

Analysis Results: {analysis_result}

Generated Visualizations: {chart_info}

Please provide a detailed, friendly response that:
1. Uses the actual column names from the dataset
2. References specific data points from both the results and sample data
3. Explains the findings in user-friendly terms
4. Naturally incorporates the generated visualizations
5. Provides context based on the data structure"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Changed from gpt-4o to gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful data analyst explaining results to a user in a conversational way."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API Error in generate_human_response: {str(e)}")  # Log the error
        return f"Error generating human-like response. Technical results: {analysis_result}"

class ChatRequest(BaseModel):
    username: str
    question: str

@router.post("/")
def chat_with_data(req: ChatRequest):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT filepath FROM files WHERE username=? ORDER BY uploaded_at DESC LIMIT 1",
        (req.username,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="No CSV uploaded yet.")

    filepath = row[0]

    # Load dataset
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # System prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/main_prompt.md")
    try:
        with open(prompt_path) as f:
            system_prompt = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="main_prompt.md missing")

    # Build prompt
    sample = df.head(5).to_dict()
    prompt = f"{system_prompt}\n\nColumns: {list(df.columns)}\nSample:\n{sample}\n\nUser: {req.question}"

    # Ask GPT
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Changed from gpt-4o to gpt-4
            messages=[{"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")  # Log the error
        raise HTTPException(
            status_code=500, 
            detail=f"OpenAI API Error: {str(e)}"
        )

    # Extract Python code
    match = re.search(r"```python(.*?)```", reply, re.DOTALL)
    python_code = match.group(1).strip() if match else None
    if not python_code:
        # Generate helpful suggestions based on the dataset
        suggestion_prompt = f"""The user asked: "{req.question}"
        Based on this dataset with columns: {list(df.columns)}, please provide:
        1. A brief explanation of why this question might be unclear
        2. 2-3 specific example questions that would work better with this dataset
        Make the response conversational and helpful."""
        
        try:
            suggestion_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a helpful data analyst"},
                         {"role": "user", "content": suggestion_prompt}]
            )
            suggestions = suggestion_response.choices[0].message.content
            
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "I couldn't generate an analysis for your question.",
                    "suggestions": suggestions,
                    "original_question": req.question
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Execute via LangGraph tool
    try:
        result, updated_state = complete_python_task.invoke({
            "graph_state": {
                "input_data": [{"variable_name": "df", "data_path": filepath}],
                "current_variables": {},
                "system_prompt": system_prompt
            },
            "thought": req.question,
            "python_code": python_code
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

    technical_result = result.strip() if result else "No textual output."
    html_paths = []
    if updated_state.get("output_image_paths"):
        print(f"Backend: Found {len(updated_state['output_image_paths'])} chart paths: {updated_state['output_image_paths']}")
        for html_file in updated_state["output_image_paths"]:
            from backend.core.chart_cleanup import record_chart_access
            html_path = f"images/plotly_figures/html/{html_file}"
            record_chart_access(html_file)  # Record that this chart was accessed
            html_paths.append(html_path)
        print(f"Backend: Returning {len(html_paths)} chart paths: {html_paths}")
    else:
        print("Backend: No output_image_paths found in updated_state")

    # Generate human-like response
    human_response = generate_human_response(
        question=req.question,
        analysis_result=technical_result,
        charts=html_paths,
        df=df
    )

    return {
        "answer": human_response,
        "technical_details": technical_result,  # Keeping original result for reference
        "charts": html_paths
    }