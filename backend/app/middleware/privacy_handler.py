import gc
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, BackgroundTasks
from ..core.privacy import PrivacyManager
logger = logging.getLogger("privacy_middleware")
class PrivacyCleanupMiddleware(BaseHTTPMiddleware):
    """Ensures memory is cleared after each chat analysis request."""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        if "/api/v1/analyze" in request.url.path:
            PrivacyManager.clear_memory()
            logger.info(f"Analysis request completed in {process_time:.2f}s. Memory cleared.")
        return response
