import json
import time
from typing import AsyncIterator, Optional

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk, ToolMessageChunk
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph

from api.core.config import settings
from api.core.logging import logger
from api.models.chat import ChatRequest
from api.prompts.prompts import SQL_AGENT_SYSTEM_PROMPT
from api.services.database_service import database_service


class AIService:
    ALLOWED_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

    def __init__(self):
        self.agent: Optional[CompiledStateGraph] = None
        self.store = InMemoryStore()

        if not settings.openai_api_key:
            logger.warning(
                "OpenAI API key not configured. Please set OPENAI_API_KEY in .env"
            )

    def _get_agent(self, model: str):
        """Get agent instance with specified model."""
        if model not in self.ALLOWED_MODELS:
            logger.warning(f"Invalid model {model}, using default")
            model = settings.openai_model

        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            openai_api_key=settings.openai_api_key,
            streaming=True,
        )

        toolkit = database_service.get_toolkit()
        db_info = database_service.get_db_info()

        return create_agent(
            model=llm,
            tools=toolkit.get_tools(),
            system_prompt=SQL_AGENT_SYSTEM_PROMPT.format(db_info=db_info),
            store=self.store,
        )

    @staticmethod
    async def _parse_model_content(chunk: AIMessageChunk) -> str:
        """Parse model content and return the text."""
        text = ""

        if hasattr(chunk, "content") and chunk.content:
            text = chunk.content

        return text

    @staticmethod
    async def _parse_tool_content(chunk: ToolMessageChunk) -> str:
        """
        Parse tool content and return the tool name and content.
        """

        tool_name = getattr(chunk, "name", None)
        tool_content = getattr(chunk, "content", None)
        tool_call_id = getattr(chunk, "tool_call_id", None)

        return {
            "tool_name": tool_name,
            "token": tool_content,
            "tool_call_id": tool_call_id,
            "done": False,
        }

    @staticmethod
    def _is_tool_message(chunk: ToolMessageChunk) -> bool:
        """
        Check if the chunk is a tool message.
        """
        tool_call_id = getattr(chunk, "tool_call_id", None)
        if tool_call_id:
            return True
        return False

    async def stream_response(self, request: ChatRequest) -> AsyncIterator[str]:
        try:
            agent = self._get_agent(request.model)

            start_time = time.time()
            async for event_tuple in agent.astream(
                input={"messages": [{"role": "user", "content": request.message}]},
                config={"configurable": {"thread_id": request.chat_id}},
                stream_mode="messages",
            ):
                chunk, _ = event_tuple
                if self._is_tool_message(chunk):
                    tool_data = await self._parse_tool_content(chunk)
                    yield f"data: {json.dumps(tool_data)}\n\n"
                else:
                    text = await self._parse_model_content(chunk)
                    yield f"data: {json.dumps({'token': text, 'done': False, 'model': request.model})}\n\n"

            end_time = time.time()
            logger.info(f"Time taken: {end_time - start_time} seconds")

            yield f"data: {json.dumps({'done': True, 'token': '', 'model': request.model})}\n\n"
        except Exception as e:
            logger.error(f"Error streaming AI service response: {str(e)}")
            raise


ai_service = AIService()
