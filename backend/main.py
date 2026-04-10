from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as analysis_router, coordinator
from app.middleware.privacy_handler import PrivacyCleanupMiddleware
from app.core.logger_config import setup_privacy_logging
import logging
from contextlib import asynccontextmanager
import os

# Initialize Privacy Logging
setup_privacy_logging(level=logging.INFO)
logger = logging.getLogger("api_main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Warm up ML models
    logger.info("Starting Moodra Engine")
    coordinator.warm_up()
    yield
    # Shutdown: Clean up if needed
    logger.info("Shutting down Moodra Engine")

app = FastAPI(
    title="Moodra - Analyzer Service",
    description="Privacy-first, local-only NLP engine for WhatsApp chat analysis.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware 
# In production on Hugging Face, set the CORS_ORIGINS env var
default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://moodra.vercel.app"
]

allowed_origins_env = os.getenv("CORS_ORIGINS", "")
allowed_origins = allowed_origins_env.split(",") if allowed_origins_env else default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Privacy Middleware (Cleans up memory after each request)
app.add_middleware(PrivacyCleanupMiddleware)

# API Routes
app.include_router(analysis_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Minimal health check to verify backend is up."""
    return {
        "status": "online",
        "service": "Moodra Engine",
        "timestamp": None
    }

if __name__ == "__main__":
    import uvicorn
    # Respect PORT env var if provided (useful for Docker/HF local testing)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, access_log=True)