from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as analysis_router
from app.middleware.privacy_handler import PrivacyCleanupMiddleware
from app.core.logger_config import setup_privacy_logging
import logging

# Initialize Privacy Logging
setup_privacy_logging(level=logging.INFO)
logger = logging.getLogger("api_main")

app = FastAPI(
    title="Expose The Chat - Analyzer Service",
    description="Privacy-first, local-only NLP engine for WhatsApp chat analysis.",
    version="1.0.0"
)

# CORS Middleware (Allow requests from local Next.js frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Privacy Middleware (Cleans up memory after each request)
app.add_middleware(PrivacyCleanupMiddleware)

# Root router for modular layout
app.include_router(analysis_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Minimal health check to verify backend is up."""
    return {
        "status": "online",
        "service": "Expose The Chat Engine",
        "timestamp": None
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Expose The Chat Engine (Local Mode)")
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=True)
