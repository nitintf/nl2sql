"""
Chat router for chatbot interactions.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.models.chat import ChatRequest, SuggestionsResponse
from api.services import ai_service
from api.services.chat_service import chat_service
from api.services.suggestion_service import suggestion_service

router = APIRouter(tags=["Chat"])


@router.post("/b/chat")
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


@router.get("/chat/suggestions", response_model=SuggestionsResponse)
async def get_suggestions():
    """
    Get query suggestions based on the database schema.

    Returns 5 interesting and useful query suggestions that users can ask.
    All suggestions are read-only SELECT queries (no mutations).
    """
    suggestions = suggestion_service.generate_suggestions()
    return SuggestionsResponse(suggestions=suggestions)


@router.post("/chat")
async def ai_chat_stream(request: ChatRequest):
    """
    Stream chat responses from the AI.

    This endpoint streams the AI's response token by token as it's generated.
    Accepts a model parameter to specify which AI model to use.
    """
    return StreamingResponse(
        ai_service.stream_response(request),
    )
