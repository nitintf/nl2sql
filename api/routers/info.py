"""
API information router.
"""

from fastapi import APIRouter
from api.models.responses import InfoResponse
from api.core.config import settings

router = APIRouter(tags=["Info"])


@router.get("/info", response_model=InfoResponse)
async def api_info() -> InfoResponse:
    """
    Get detailed API information.
    """
    return InfoResponse(
        name=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        debug_mode=settings.debug,
        api_prefix=settings.api_v1_prefix,
    )
