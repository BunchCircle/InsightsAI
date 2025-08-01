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

# Verify required environment variables
required_env_vars = ["OPENAI_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please set these variables in Railway's environment variables section")
else:
    logger.info("All required environment variables are present")

app = FastAPI(title="Insights API")

@app.get("/health")
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

# Serve Next.js frontend
try:
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "insights-frontend", "out")
    if not os.path.exists(frontend_dir):
        logger.warning(f"Frontend directory not found at {frontend_dir}")
        # Try relative to current working directory
        frontend_dir = os.path.join(os.getcwd(), "insights-frontend", "out")
        if not os.path.exists(frontend_dir):
            logger.warning(f"Frontend directory not found at {frontend_dir}")
            raise FileNotFoundError(f"Frontend directory not found at {frontend_dir}")
    
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    logger.info(f"Frontend static files mounted successfully from {frontend_dir}")
except Exception as e:
    logger.error(f"Error mounting frontend files: {str(e)}")
    # Don't fail startup if frontend files aren't available yet