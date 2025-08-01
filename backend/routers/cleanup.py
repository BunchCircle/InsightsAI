from fastapi import APIRouter, HTTPException
import os
import shutil

router = APIRouter()

@router.post("/reload")
async def handle_page_reload():
    """Handle page reload by cleaning up all charts"""
    charts_dir = "images/plotly_figures/html"
    metadata_file = "images/plotly_figures/metadata.json"
    
    try:
        # Remove and recreate the charts directory
        if os.path.exists(charts_dir):
            shutil.rmtree(charts_dir)
        os.makedirs(charts_dir, exist_ok=True)
        
        # Clear the metadata file
        if os.path.exists(metadata_file):
            with open(metadata_file, "w") as f:
                f.write("{}")
                
        return {"message": "Charts cleaned up successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
