from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.routers import auth, upload, chat, cleanup
from fastapi.staticfiles import StaticFiles
import os

load_dotenv()

app = FastAPI(title="Insights API")



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