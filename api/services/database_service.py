from typing import Optional

from langchain_openai import ChatOpenAI
from api.core.config import settings
from api.core.logging import logger
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

from api.services.sql_service import CustomSQLDatabaseToolkit


class DatabaseService:
    """Service for database operations."""

    def __init__(self):
        self._db_info_cache = None
        self._usable_tables_cache = None
        self.db: Optional[SQLDatabase] = None
        self.toolkit: Optional[SQLDatabaseToolkit] = None

        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            openai_api_key=settings.openai_api_key,
            streaming=False,
            max_retries=0,
        )

        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection and LangChain components."""
        try:
            # db_uri = f"postgresql://postgres:nitin123@db.oihylrqyqljixpcnouce.supabase.co:5432/postgres"
            db_uri = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
            self.db = SQLDatabase.from_uri(db_uri)
            logger.info(f"Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database service: {str(e)}")
            raise

    def get_db_info(self):
        if self._db_info_cache is None:
            self._db_info_cache = self.db.get_context()
        return self._db_info_cache

    def get_usable_tables(self):
        if self._usable_tables_cache is None:
            self._usable_tables_cache = self.db.get_usable_table_names()
        return self._usable_tables_cache

    def get_toolkit(self):
        if not self.toolkit:
            self.toolkit = CustomSQLDatabaseToolkit(db=self.db, llm=self.llm)
        return self.toolkit


database_service = DatabaseService()
