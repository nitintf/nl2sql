"""
Health check router.
"""

from fastapi import APIRouter
from api.models.responses import HealthResponse, RootResponse
from api.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/", response_model=RootResponse)
async def root() -> RootResponse:
    """
    Root endpoint - API information.
    """
    return RootResponse(
        message="Welcome to NL2SQL API",
        version=settings.app_version,
        docs="/docs",
        redoc="/redoc",
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns the current status of the API.
    """
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
    )
