"""
Service for generating query suggestions based on database schema.
"""

from langchain_openai import ChatOpenAI

from api.core.config import settings
from api.core.logging import logger
from api.services.sql_service import sql_service
from api.prompts.sql_prompts import get_suggestion_generation_prompt
from api.models.chat import SuggestionsResponse


class SuggestionService:
    """Service for generating database query suggestions."""

    def __init__(self):
        """Initialize the suggestion service."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            openai_api_key=settings.openai_api_key,
            streaming=False,
            max_retries=0,
        )

    def generate_suggestions(self):
        """
        Generate 5 query suggestions based on the database schema.

        Returns:
            List of suggestion dictionaries with 'question' and 'description' keys
        """
        try:
            # Get table information
            table_info = sql_service.get_table_info()
            usable_tables = sql_service.get_usable_tables()

            if not table_info:
                logger.warning("No table information available")
                return []

            structured_llm = self.llm.with_structured_output(SuggestionsResponse)
            suggestion_prompt = get_suggestion_generation_prompt()
            suggestion_chain = suggestion_prompt | structured_llm

            result = suggestion_chain.invoke(
                {
                    "table_info": table_info,
                    "table_names": ", ".join(usable_tables),
                }
            )

            return result.suggestions

        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []


# Global service instance
suggestion_service = SuggestionService()
