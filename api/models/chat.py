"""
Chat models for chatbot endpoints.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., description="User's chat message", min_length=1)
    model: str = Field(
        default="gpt-4o-mini", description="Model to use for the chat response"
    )
    chat_id: str = Field(..., description="Chat ID", min_length=1)
