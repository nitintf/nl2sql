"""
Chat service for streaming responses using SQL tools with LangChain agent.
"""

import json
import time
from typing import AsyncIterator
from typing import Optional

from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph

from api.core.config import settings
from api.core.logging import logger
from api.services.sql_service import sql_service
from api.prompts.sql_prompts import get_answer_generation_prompt
from api.tools.sql_tools import (
    generate_sql_query_tool,
    validate_sql_query_tool,
    execute_sql_query_tool,
)


class ChatService:
    """Service for handling chat streaming responses using SQL tools."""

    ALLOWED_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

    def __init__(self):
        self.llm: Optional[ChatOpenAI] = None
        self.agent: Optional[CompiledStateGraph] = None

        if not settings.openai_api_key:
            logger.warning(
                "OpenAI API key not configured. Please set OPENAI_API_KEY in .env"
            )

        self._initialize_agent()

    def _initialize_agent(self):
        try:
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
                openai_api_key=settings.openai_api_key,
                max_retries=1,
                streaming=True,
            )

            tools = [
                generate_sql_query_tool,
                validate_sql_query_tool,
                execute_sql_query_tool,
            ]

            #             prompt = ChatPromptTemplate.from_messages(
            #                 [
            #                     (
            #                         "ai",
            #                         """You are a SQL assistant. When users ask questions about the database, you can use these tools if needed in this order:
            # 1. generate_sql_query - Convert natural language questions to SQL
            # 2. validate_sql_query - Check if the query is safe to execute (only SELECT queries allowed)
            # 3. execute_sql_query - Execute validated SQL queries and get results

            # After getting results, provide a natural language answer based on the data.""",
            #                     ),
            #                     # MessagesPlaceholder(variable_name="chat_history"),
            #                     ("human", "{input}"),
            #                 ]
            #             )

            self.agent = create_agent(model=self.llm, tools=tools)

            logger.info("Chat service agent initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing chat service agent: {str(e)}")
            raise

    async def stream_response(
        self, user_message: str, model: str = "gpt-4o-mini", chat_id: str = ""
    ) -> AsyncIterator[str]:
        if not sql_service.db:
            error_data = {
                "token": "Database not configured. Please configure database credentials.",
                "done": False,
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        try:
            start_time = time.time()

            if model not in self.ALLOWED_MODELS:
                logger.warning(f"Invalid model {model}, using default")
                model = settings.openai_model

            model_data = {"token": "", "done": False, "model": model, "type": "model"}
            yield f"data: {json.dumps(model_data)}\n\n"

            # Get chat history for memory
            memory = sql_service.get_memory(chat_id)
            chat_history = memory.messages

            # Prepare input for agent
            agent_input = {
                "input": user_message,
                "chat_history": chat_history,
            }

            # Stream agent execution
            sql_query = None
            sql_result = None
            validation_result = None

            tools = [
                generate_sql_query_tool,
                validate_sql_query_tool,
                execute_sql_query_tool,
            ]

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are a SQL assistant. When users ask questions about the database, you can use these tools if needed in this order:
1. generate_sql_query - Convert natural language questions to SQL
2. validate_sql_query - Check if the query is safe to execute (only SELECT queries allowed)
3. execute_sql_query - Execute validated SQL queries and get results

After getting results, provide a natural language answer based on the data.""",
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

            async for event in self.agent.astream(agent_input, stream_mode="messages"):
                # Handle tool calls
                if event["event"] == "on_tool_start":
                    tool_name = event["name"]
                    tool_input = event.get("data", {}).get("input", {})

                    if tool_name == "generate_sql_query":
                        sql_query = tool_input.get("question", "")
                        if sql_query:
                            tool_chunk_data = {
                                "token": sql_query,
                                "tool_name": "sql_query",
                                "done": False,
                                "type": "tool",
                            }
                            yield f"data: {json.dumps(tool_chunk_data)}\n\n"

                    elif tool_name == "validate_sql_query":
                        validation_result = event.get("data", {}).get("output", "")
                        if "NOT safe" in validation_result:
                            # Format query in markdown code block
                            formatted_query = f"\n{sql_query}\n```"
                            error_data = {
                                "token": f"Cannot execute query: {validation_result}\n\n**Query:**\n{formatted_query}",
                                "done": False,
                                "type": "model",
                            }
                            yield f"data: {json.dumps(error_data)}\n\n"
                            final_chunk_data = {"token": "", "done": True}
                            yield f"data: {json.dumps(final_chunk_data)}\n\n"
                            return

                    elif tool_name == "execute_sql_query":
                        sql_result = event.get("data", {}).get("output", "")
                        if sql_result:
                            execution_tool_data = {
                                "token": str(sql_result),
                                "tool_name": "sql_execution_result",
                                "done": False,
                                "type": "tool",
                            }
                            yield f"data: {json.dumps(execution_tool_data)}\n\n"

                # Handle model responses (final answer)
                elif event["event"] == "on_chain_stream":
                    if event.get("name") == "AgentExecutor":
                        chunk = event.get("chunk", {})
                        if "messages" in chunk:
                            for message in chunk["messages"]:
                                if hasattr(message, "content") and message.content:
                                    token = message.content
                                    chunk_data = {
                                        "token": token,
                                        "done": False,
                                        "type": "model",
                                    }
                                    yield f"data: {json.dumps(chunk_data)}\n\n"

            # Add to memory
            if sql_result:
                result_text = f"Query: {sql_query}\nResult: {sql_result}"
                sql_service.add_to_memory(chat_id, user_message, result_text)

            final_chunk_data = {"token": "", "done": True}
            yield f"data: {json.dumps(final_chunk_data)}\n\n"

            end_time = time.time()
            logger.info(
                f"Processed NL2SQL query in {end_time - start_time:.2f} seconds"
            )

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            error_data = {
                "token": f"An error occurred: {str(e)}. Please try again later.",
                "done": False,
            }
            yield f"data: {json.dumps(error_data)}\n\n"


chat_service = ChatService()  ## Changes
