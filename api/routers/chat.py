"""
Chat router for chatbot interactions.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.models.chat import ChatRequest
from api.services.chat import chat_service

router = APIRouter(tags=["Chat"])


@router.post("/chat")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from the AI.

    This endpoint streams the AI's response token by token as it's generated.
    Accepts a model parameter to specify which AI model to use.
    """

    return StreamingResponse(
        chat_service.stream_response(request.message, request.model, request.chat_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
