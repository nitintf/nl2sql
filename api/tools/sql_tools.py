"""
SQL tools for LangChain agent.
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain.tools import tool
from api.services.sql_service import sql_service


class GenerateSQLQueryInput(BaseModel):
    question: str = Field(
        ..., description="Natural language question to convert to SQL"
    )
    chat_id: str = Field(..., description="Chat session ID for memory")


def generate_sql_query_tool(llm: Optional[ChatOpenAI] = None):
    """Factory function to create tool with optional LLM."""

    @tool(
        "generate_sql_query",
        description="Generate a SQL SELECT query from a natural language question. Use this first to convert user questions to SQL.",
        args_schema=GenerateSQLQueryInput,
    )
    def _generate_sql_query_tool(input: GenerateSQLQueryInput) -> str:
        return sql_service.generate_sql_query(input.question, input.chat_id, llm=llm)

    return _generate_sql_query_tool


class ValidateSQLQueryInput(BaseModel):
    query: str = Field(..., description="SQL query to validate")


def validate_sql_query_tool(llm: Optional[ChatOpenAI] = None):
    """Factory function to create tool with optional LLM."""

    @tool(
        "validate_sql_query",
        description="Validate if a SQL query is safe to execute. Only SELECT queries are allowed. Returns validation result with reason.",
        args_schema=ValidateSQLQueryInput,
    )
    def _validate_sql_query_tool(input: ValidateSQLQueryInput) -> str:
        can_execute, reason = sql_service.validate_query(input.query, llm=llm)
        if can_execute:
            return f"Query is safe to execute: {reason}"
        else:
            return f"Query is NOT safe: {reason}"

    return _validate_sql_query_tool


class ExecuteSQLQueryInput(BaseModel):
    query: str = Field(..., description="Validated SQL SELECT query to execute")


@tool(
    "execute_sql_query",
    description="Execute a validated SQL SELECT query and return results. Only use this after validating the query.",
    args_schema=ExecuteSQLQueryInput,
)
def execute_sql_query_tool(input: ExecuteSQLQueryInput) -> str:
    """Execute SQL query and return results."""
    return sql_service.execute_sql_query(input.query)
