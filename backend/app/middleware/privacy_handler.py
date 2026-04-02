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
        
        # Don't log the body for security
        # request_body = await request.body() # NO: This would consume the stream and could be logged
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # If the request was an analysis endpoint, we trigger a cleanup
        if "/api/v1/analyze" in request.url.path:
            # We use gc.collect() immediately after response
            # Better to do it after response is sent
            # But in local env, sequential is fine
            PrivacyManager.clear_memory()
            
            # Log only operational metadata
            logger.info(f"Analysis request completed in {process_time:.2f}s. Memory cleared.")
            
        return response
