"""
SQL service for database operations, query generation, and validation.
"""

from typing import Dict, List, Optional, Tuple

from langchain_classic.chains import create_sql_query_chain
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory as ChatMessageHistory
from pydantic import BaseModel, Field

from api.core.config import settings
from api.core.logging import logger
from api.utils.sql_utils import clean_sql_query
from api.prompts.sql_prompts import (
    get_example_prompt,
    get_sql_query_generation_prompt,
    get_query_validation_prompt,
)


class Table(BaseModel):
    """Table in SQL database."""

    name: List[str] = Field(description="List of Name of tables in SQL database.")


class QueryValidationResult(BaseModel):
    """Result of SQL query validation."""

    can_execute: bool = Field(
        description="True if the query should be executed, False otherwise"
    )
    reason: str = Field(
        description="Brief explanation of why the query can or cannot be executed including the query"
    )


# Few-shot examples for SQL query generation
FEW_SHOT_EXAMPLES = [
    {
        "input": "List all customers in France with a credit limit over 20,000.",
        "query": "SELECT * FROM customers WHERE country = 'France' AND creditLimit > 20000;",
    },
    {
        "input": "Get the highest payment amount made by any customer.",
        "query": "SELECT MAX(amount) FROM payments;",
    },
    {
        "input": "Show product details for products in the 'Motorcycles' product line.",
        "query": "SELECT * FROM products WHERE productLine = 'Motorcycles';",
    },
    {
        "input": "Retrieve the names of employees who report to employee number 1002.",
        "query": "SELECT firstName, lastName FROM employees WHERE reportsTo = 1002;",
    },
    {
        "input": "List all products with a stock quantity less than 7000.",
        "query": "SELECT productName, quantityInStock FROM products WHERE quantityInStock < 7000;",
    },
    {
        "input": "what is price of `1968 Ford Mustang`",
        "query": "SELECT `buyPrice`, `MSRP` FROM products WHERE `productName` = '1968 Ford Mustang' LIMIT 1;",
    },
]


class SQLService:
    """Service for SQL database operations, query generation, and validation."""

    def __init__(self):
        self.db: Optional[SQLDatabase] = None
        self.llm: Optional[ChatOpenAI] = None
        self.generate_query = None
        self.execute_query = None
        self.memory_store: Dict[str, ChatMessageHistory] = {}

        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection and LangChain components."""
        try:
            db_uri = f"postgresql://postgres:nitin123@db.oihylrqyqljixpcnouce.supabase.co:5432/postgres"

            self.db = SQLDatabase.from_uri(db_uri)
            logger.info(f"Connected to database: {settings.db_name}")

            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
                openai_api_key=settings.openai_api_key,
                streaming=True,
                max_retries=2,
            )

            table_info = self.get_table_info()
            example_prompt = get_example_prompt()

            few_shot_prompt = FewShotChatMessagePromptTemplate(
                example_prompt=example_prompt,
                examples=FEW_SHOT_EXAMPLES,
                input_variables=["input", "top_k", "table_info"],
            )

            sql_query_prompt = get_sql_query_generation_prompt(table_info)

            final_prompt = ChatPromptTemplate.from_messages(
                [
                    *sql_query_prompt.messages,
                    few_shot_prompt,
                    MessagesPlaceholder(variable_name="messages"),
                    ("human", "{input}"),
                ]
            )

            self.generate_query = create_sql_query_chain(
                self.llm, self.db, final_prompt
            )

            self.execute_query = QuerySQLDataBaseTool(db=self.db)

            logger.info("SQL service initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing SQL service: {str(e)}")
            raise

    def get_memory(self, chat_id: str) -> ChatMessageHistory:
        """Get or create memory for a chat session."""
        if chat_id not in self.memory_store:
            self.memory_store[chat_id] = ChatMessageHistory()
        return self.memory_store[chat_id]

    def validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Use LLM to validate if a SQL query should be executed.

        Args:
            query: The SQL query to validate

        Returns:
            Tuple of (is_valid, explanation)
            - is_valid: True if query should be executed, False otherwise
            - explanation: Explanation of why query can/cannot be executed
        """
        validation_prompt = get_query_validation_prompt()

        structured_llm = self.llm.with_structured_output(QueryValidationResult)
        validation_chain = validation_prompt | structured_llm

        try:
            validation_result = validation_chain.invoke({"query": query})
            return validation_result.can_execute, validation_result.reason

        except Exception as e:
            logger.error(f"Error in LLM validation: {str(e)}")
            return False, f"Validation error: {str(e)}"

    def execute_sql_query(self, query: str) -> str:
        """
        Execute a SQL query with error handling and logging.

        Args:
            query: The SQL query to execute

        Returns:
            The query result as a string

        Raises:
            Exception: If query execution fails
        """
        try:
            logger.info(f"Executing SQL query: {query}")
            result = self.execute_query.invoke(query)
            return result
        except Exception as e:
            error_msg = f"Error executing SQL query: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Failed query: {query}")
            raise

    def generate_sql_query(self, user_message: str, chat_id: str) -> str:
        """
        Generate a SQL query from a natural language question.

        Args:
            user_message: The user's natural language question
            chat_id: The chat session ID for memory

        Returns:
            The generated SQL query
        """
        memory = self.get_memory(chat_id)
        chain_input = {
            "question": user_message,
            "messages": memory.messages,
        }

        query_chain = RunnablePassthrough.assign(
            query=self.generate_query | RunnableLambda(clean_sql_query)
        )

        query_result = query_chain.invoke(chain_input)
        return query_result.get("query", "")

    def get_table_info(self) -> str:
        """Get table information from the database."""
        if not self.db:
            return ""
        return self.db.table_info

    def get_usable_tables(self) -> List[str]:
        """Get list of usable table names."""
        if not self.db:
            return []
        return self.db.get_usable_table_names()

    def add_to_memory(self, chat_id: str, user_message: str, ai_message: str):
        """Add messages to chat memory."""
        memory = self.get_memory(chat_id)
        memory.add_user_message(user_message)
        memory.add_ai_message(ai_message)


# Global service instance
sql_service = SQLService()
