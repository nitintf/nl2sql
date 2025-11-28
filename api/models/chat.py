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


class QuerySuggestion(BaseModel):
    """A single query suggestion."""

    question: str = Field(description="Natural language question that can be asked")


class SuggestionsResponse(BaseModel):
    """Response containing query suggestions."""

    suggestions: list[QuerySuggestion] = Field(
        description="List of 5 query suggestions"
    )
