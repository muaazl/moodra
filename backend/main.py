from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as analysis_router, coordinator
from app.middleware.privacy_handler import PrivacyCleanupMiddleware
from app.core.logger_config import setup_privacy_logging
import logging
from contextlib import asynccontextmanager
import os
setup_privacy_logging(level=logging.INFO)
logger = logging.getLogger("api_main")
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Moodra Engine (Local Mode)")
    coordinator.warm_up()
    yield
    logger.info("Shutting down Moodra Engine")
app = FastAPI(
    title="Moodra - Analyzer Service",
    description="Privacy-first, local-only NLP engine for WhatsApp chat analysis.",
    version="1.0.0",
    lifespan=lifespan
)
cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PrivacyCleanupMiddleware)
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
    logger.info("Starting Moodra Engine (Local Mode)")
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=True)
