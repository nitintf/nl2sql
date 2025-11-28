from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import (
    QuerySQLDataBaseTool,
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
)
from langchain.tools import BaseTool
from typing import List
import re


class CustomQuerySQLDataBaseTool(QuerySQLDataBaseTool):
    """Custom tool that returns only results, not SQL queries."""

    def _run(self, query: str) -> str:
        """Execute SQL and return ONLY results, not the query itself."""
        query = self._clean_query(query)

        if not self._is_safe_query(query):
            return "Error: Only SELECT queries are allowed for security reasons."

        try:
            result = self.db.run(query)

            if not result or result.strip() == "":
                return "No results found."

            return result
        except Exception as e:
            return f"Error executing query: {str(e)}"

    def _clean_query(self, query: str) -> str:
        """Clean SQL query from markdown and formatting."""
        query = re.sub(r"```sql\s*", "", query, flags=re.IGNORECASE)
        query = re.sub(r"```\s*", "", query)
        query = re.sub(r"^(SQL Query:|Query:)\s*", "", query, flags=re.IGNORECASE)
        return query.strip().rstrip(";")

    def _is_safe_query(self, query: str) -> bool:
        """Validate query is safe (SELECT only)."""
        query_upper = query.strip().upper()

        dangerous = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "TRUNCATE",
            "ALTER",
            "CREATE",
            "REPLACE",
            "MERGE",
            "GRANT",
            "REVOKE",
            "EXEC",
            "EXECUTE",
        ]

        return not any(
            re.search(rf"\b{keyword}\b", query_upper) for keyword in dangerous
        )


class CustomSQLDatabaseToolkit(SQLDatabaseToolkit):
    """Custom toolkit with tools that don't expose SQL queries."""

    def get_tools(self) -> List[BaseTool]:
        """Get tools with custom query tool that hides SQL."""

        query_tool = CustomQuerySQLDataBaseTool(db=self.db)
        query_tool.name = "sql_db_query"
        query_tool.description = (
            "Execute a SQL query against the database and get back results. "
            "Input should be a valid SQL SELECT query. "
            "Returns only the query results."
        )

        list_tables_tool = ListSQLDatabaseTool(db=self.db)
        list_tables_tool.description = (
            "List available tables in the database. "
            "Use this to see what data is available. "
            "Input is an empty string."
        )

        schema_tool = InfoSQLDatabaseTool(db=self.db)
        schema_tool.description = (
            "Get schema information for specified tables. "
            "Input is a comma-separated list of table names. "
            "Use this to understand table structure before querying."
        )

        return [
            query_tool,
            schema_tool,
            list_tables_tool,
        ]
