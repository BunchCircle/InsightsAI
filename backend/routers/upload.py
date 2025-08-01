from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import shutil
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def validate_csv(df: pd.DataFrame) -> tuple[bool, list[str]]:
    issues = []

    # Check for infinite values
    numeric_cols = df.select_dtypes(include=np.number).columns
    if not numeric_cols.empty:
        inf_columns = numeric_cols[np.isinf(df[numeric_cols]).any()].tolist()
        if inf_columns:
            issues.append(f"Infinite values found in columns: {', '.join(inf_columns)}")

    # Check column names for special characters
    special_char_columns = [col for col in df.columns if not col.replace('_', '').replace(' ', '').isalnum()]
    if special_char_columns:
        issues.append(f"Special characters found in column names: {', '.join(special_char_columns)}")

    # Check for mixed data types in numeric columns
    for col in numeric_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            non_numeric = df[col].apply(lambda x: not (pd.isna(x) or isinstance(x, (int, float))))
            if non_numeric.any():
                issues.append(f"Mixed data types found in numeric column: {col}")

    return len(issues) == 0, issues

@router.post("/")
def upload_file(
    username: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    file_path = UPLOAD_DIR / file.filename

    # Save file temporarily
    temp_path = UPLOAD_DIR / f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Validate CSV
    try:
        df = pd.read_csv(temp_path, low_memory=False)

        # Clean inf values
        df = df.replace([np.inf, -np.inf], np.nan)

        # Track null columns before replacing
        null_columns = df.columns[df.isnull().any()].tolist()

        # Replace nulls with "null" string for consistency
        df = df.fillna("null")

        is_valid, issues = validate_csv(df)

        preview = df.head(5).to_dict(orient="records")
        columns = list(df.columns)

        # Always move file even if cleaning was required
        shutil.move(temp_path, file_path)

        # Persist in DB
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO files (username, filename, filepath) VALUES (?,?,?)",
            (username, file.filename, str(file_path))
        )
        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "File uploaded successfully. Missing values were filled with 'null' to ensure consistency." if null_columns else "File uploaded successfully.",
            "filled_null_columns": null_columns,
            "filename": file.filename,
            "preview": preview,
            "columns": columns
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"CSV read error: {e}")