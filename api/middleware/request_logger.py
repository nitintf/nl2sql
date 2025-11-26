"""
Request logging middleware.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from api.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and their processing time."""

    async def dispatch(self, request: Request, call_next):
        """Log request and response details."""
        start_time = time.time()

        # Log request
        logger.info(f"➡️  {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Log response time
        process_time = time.time() - start_time
        logger.info(
            f"⬅️  {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.3f}s"
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response
