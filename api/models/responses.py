"""
Response models for API endpoints.
"""

from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    """Response model for root endpoint."""

    message: str = Field(..., description="Welcome message")
    version: str = Field(..., description="API version")
    docs: str = Field(..., description="Documentation URL")
    redoc: str = Field(..., description="ReDoc URL")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class InfoResponse(BaseModel):
    """Response model for info endpoint."""

    name: str = Field(..., description="API name")
    version: str = Field(..., description="API version")
    description: str = Field(..., description="API description")
    debug_mode: bool = Field(..., description="Whether debug mode is enabled")
    api_prefix: str = Field(..., description="API version prefix")
