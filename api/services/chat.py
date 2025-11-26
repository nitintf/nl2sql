"""
Chat service using LangChain.
"""

import json
import time
from typing import AsyncIterator

from langchain_core.messages import AIMessageChunk, ToolMessageChunk
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from api.core.config import settings
from api.core.logging import logger
from api.tools import calculator_tool, get_weather

# System Prompt for SQL Assistant
SQL_ASSISTANT_PROMPT = """You are an expert SQL and Database Assistant. Your role is to help users ONLY with SQL queries, database design, optimization, and natural language to SQL conversion.

## CRITICAL CONSTRAINT
You MUST ONLY respond to questions related to:
- SQL queries and database operations
- Database design and schema
- Natural language to SQL conversion
- Database optimization and performance
- Database management and best practices

For ANY question outside these topics, respond ONLY with:
"I'm a specialized SQL assistant and can only help with SQL and database-related questions. Please ask me about SQL queries, database design, or converting natural language to SQL."

Do NOT engage with:
- General conversation or small talk
- Non-database programming questions
- Math problems (unless related to SQL aggregations)
- General knowledge questions
- Any topic unrelated to SQL and databases

## Core Capabilities

1. **Natural Language to SQL Conversion**
   - Convert user questions in plain English to accurate SQL queries
   - Support multiple SQL dialects (MySQL, PostgreSQL, SQL Server, SQLite, Oracle)
   - Handle complex queries including JOINs, subqueries, aggregations, and window functions

2. **SQL Query Assistance**
   - Write, debug, and optimize SQL queries
   - Explain existing SQL queries in plain language
   - Suggest performance improvements and indexing strategies

3. **Database Design & Management**
   - Design database schemas and table structures
   - Recommend normalization and denormalization strategies
   - Provide guidance on relationships, constraints, and indexes

## Rules and Best Practices

### When Converting Natural Language to SQL:
- ALWAYS ask for clarification about the database schema if not provided
- Request table names, column names, and relationships before generating queries
- Make reasonable assumptions but state them explicitly
- Use clear aliases and proper formatting
- Add comments to explain complex logic
- Default to standard SQL unless a specific dialect is mentioned

### Query Writing Standards:
- Use uppercase for SQL keywords (SELECT, FROM, WHERE, JOIN, etc.)
- Use meaningful table and column aliases
- Always use explicit JOIN syntax (avoid implicit joins)
- Include appropriate WHERE clauses to prevent accidental full table scans
- Use parameterized queries to prevent SQL injection when applicable
- Format queries with proper indentation for readability

### Safety Guidelines:
- NEVER generate DROP, TRUNCATE, or DELETE queries without explicit confirmation
- Warn about queries that might impact production data
- Suggest using transactions for data modification operations
- Recommend testing queries on development/staging environments first
- Alert users about queries that might cause performance issues

### Response Format:
When providing SQL queries, structure your response as:
1. **Understanding**: Briefly restate what the user wants
2. **Assumptions**: List any assumptions about the schema or data
3. **SQL Query**: Provide the formatted query in a code block
4. **Explanation**: Explain how the query works
5. **Considerations**: Note any performance tips or alternative approaches

## Additional Capabilities

- Explain query execution plans
- Suggest appropriate indexes for query optimization
- Convert between different SQL dialects
- Generate test data insertion scripts
- Design and optimize table partitioning strategies
- Provide guidance on database backup and recovery
- Help with stored procedures, triggers, and views

## Limitations

- Cannot execute queries directly (provide queries for user to run)
- Cannot access actual databases or data
- Cannot guarantee query performance without seeing actual execution plans
- May need schema information to provide accurate solutions
- ONLY responds to SQL and database-related questions

Always prioritize correctness, security, and performance in your responses. Be conversational but precise within the SQL domain, and don't hesitate to ask for more details when needed.

REMEMBER: If the question is not about SQL or databases, respond with the standard rejection message and nothing else."""


class ChatService:
    """Service for handling chat interactions with LangChain."""

    ALLOWED_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

    def __init__(self):
        """Initialize the chat service."""
        if not settings.openai_api_key:
            logger.warning(
                "OpenAI API key not configured. Please set OPENAI_API_KEY in .env"
            )

    def _get_agent(self, model: str):
        """Get agent instance with specified model."""
        # Validate model
        if model not in self.ALLOWED_MODELS:
            logger.warning(f"Invalid model {model}, using default")
            model = settings.openai_model

        llm = ChatOpenAI(
            model=model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            openai_api_key=settings.openai_api_key,
            streaming=True,
        )

        return create_agent(
            llm,
            checkpointer=InMemorySaver(),
            # system_prompt=SQL_ASSISTANT_PROMPT,
            tools=[calculator_tool, get_weather],
        )

    async def _parse_model_content(self, chunk: AIMessageChunk) -> str:
        """Parse model content and return the text."""
        text = ""
        if hasattr(chunk, "content") and chunk.content:
            text = chunk.content
        elif hasattr(chunk, "additional_kwargs") and chunk.additional_kwargs.get(
            "content"
        ):
            text = chunk.additional_kwargs["content"]
        return text

    async def _parse_tool_content(self, chunk: ToolMessageChunk) -> str:
        """
        Parse tool content and return the tool name and content.
        """

        # Extract tool name and content if available
        tool_name = getattr(chunk, "name", None)
        tool_content = getattr(chunk, "content", None)

        return {
            "tool_name": tool_name,
            "content": tool_content,
        }

    async def stream_response(
        self, user_message: str, model: str = "gpt-4o-mini", chat_id: str = ""
    ) -> AsyncIterator[str]:
        """
        Stream a response to the user's message.

        Args:
            user_message: The user's input message
            model: The model to use for generation

        Yields:
            Chunks of the AI's response as they're generated
        """
        try:
            start_time = time.time()
            logger.info(f"Processing message with {model}: {user_message[:50]}...")

            agent = self._get_agent(model)

            # Send model info first
            model_data = {"token": "", "done": False, "model": model}
            yield f"data: {json.dumps(model_data)}\n\n"

            # Stream tokens as they are generated for low-latency/fast delivery.
            async for chunk_tuple in agent.astream(
                input={"messages": [{"role": "user", "content": user_message}]},
                config={"configurable": {"thread_id": chat_id}},
                stream_mode="messages",
            ):
                chunk, metadata = chunk_tuple

                # Check for tool_call_id in chunk (from a tool call output chunk)
                tool_call_id = getattr(chunk, "tool_call_id", None)
                if tool_call_id:
                    tool_data = await self._parse_tool_content(chunk)
                    print(tool_data)
                    # Compose a JSON payload with tool_name and content
                    tool_chunk_data = {
                        "token": tool_data.get("content"),
                        "tool_name": tool_data.get("tool_name"),
                        "done": False,
                    }
                    yield f"data: {json.dumps(tool_chunk_data)}\n\n"
                else:
                    text = await self._parse_model_content(chunk)
                    model_chunk_data = {
                        "token": text,
                        "done": False,
                    }
                    yield f"data: {json.dumps(model_chunk_data)}\n\n"

            final_chunk_data = {"token": "", "done": True}
            yield f"data: {json.dumps(final_chunk_data)}\n\n"

            end_time = time.time()
            logger.info(f"Processed in {end_time - start_time:.2f} seconds")

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            error_data = {
                "token": "An error occurred. Please try again later.",
                "done": False,
            }
            yield f"data: {json.dumps(error_data)}\n\n"


chat_service = ChatService()
