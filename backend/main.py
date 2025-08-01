from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.routers import auth, upload, chat, cleanup
from fastapi.staticfiles import StaticFiles
import os

load_dotenv()

app = FastAPI(title="Insights API")

@app.get("/")
async def health_check():
    """Health check endpoint for Railway deployment"""
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

# Static charts mounted at /images
app.mount("/images", StaticFiles(directory="images"), name="images")

# API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(chat.router,   prefix="/api/chat",   tags=["Chat"])
app.include_router(cleanup.router, prefix="/api/cleanup", tags=["Cleanup"])