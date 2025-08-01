from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

app = FastAPI(title="Insights API")

@app.get("/")
async def health_check():
    """Health check endpoint for Railway deployment"""
    logger.info("Health check endpoint called")
    return {"status": "healthy", "message": "Insights API is running"}

# Create necessary directories on startup
def create_required_directories():
    directories = [
        "uploads",
        "images/plotly_figures/html",
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Initialize metadata.json if it doesn't exist
    metadata_path = "images/plotly_figures/metadata.json"
    if not os.path.exists(metadata_path):
        with open(metadata_path, "w") as f:
            f.write("{}")

create_required_directories()


# CORS: allow Next.js dev server (port 3000) and production build
origins = [
    "*",  # Allow all origins for development. Change to specific domains in production.
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with error handling
try:
    app.mount("/images", StaticFiles(directory="images"), name="images")
    logger.info("Static files mounted successfully")
except Exception as e:
    logger.error(f"Error mounting static files: {str(e)}")
    # Don't fail startup if static files aren't available yet

# Import and mount API routers with error handling
try:
    from backend.routers import auth, upload, chat, cleanup
    
    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
    app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
    app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
    app.include_router(cleanup.router, prefix="/api/cleanup", tags=["Cleanup"])
    logger.info("All API routers mounted successfully")
except Exception as e:
    logger.error(f"Error mounting API routers: {str(e)}")
    # Don't fail startup if API routers have an issue