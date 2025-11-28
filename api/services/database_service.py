from typing import Optional

from langchain_openai import ChatOpenAI
from api.core.logging import logger
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit


class DatabaseService:
    """Service for database operations."""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.db: Optional[SQLDatabase] = None
        self.toolkit: Optional[SQLDatabaseToolkit] = None
        self.llm: Optional[ChatOpenAI] = llm

        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection and LangChain components."""
        try:
            db_uri = f"postgresql://postgres:nitin123@db.oihylrqyqljixpcnouce.supabase.co:5432/postgres"
            self.db = SQLDatabase.from_uri(db_uri)
        except Exception as e:
            logger.error(f"Error initializing database service: {str(e)}")
            raise

    def get_db_info(self):
        return self.db.get_context()

    def get_toolkit(self):
        if not self.toolkit:
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        return self.toolkit


database_service = DatabaseService()
