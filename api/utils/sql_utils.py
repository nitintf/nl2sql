"""
SQL utility functions for cleaning and processing SQL queries.
"""

import re
from typing import List


def clean_sql_query(text: str) -> str:
    """
    Clean SQL query by removing code block syntax, various SQL tags, backticks,
    prefixes, and unnecessary whitespace while preserving the core SQL query.

    Args:
        text (str): Raw SQL query text that may contain code blocks, tags, and backticks

    Returns:
        str: Cleaned SQL query
    """
    # Step 1: Remove code block syntax and any SQL-related tags
    # This handles variations like ```sql, ```SQL, ```SQLQuery, etc.
    block_pattern = r"```(?:sql|SQL|SQLQuery|mysql|postgresql)?\s*(.*?)\s*```"
    text = re.sub(block_pattern, r"\1", text, flags=re.DOTALL)

    # Step 2: Handle "SQLQuery:" prefix and similar variations
    # This will match patterns like "SQLQuery:", "SQL Query:", "MySQL:", etc.
    prefix_pattern = r"^(?:SQL\s*Query|SQLQuery|MySQL|PostgreSQL|SQL)\s*:\s*"
    text = re.sub(prefix_pattern, "", text, flags=re.IGNORECASE)

    # Step 3: Extract the first SQL statement if there's random text after it
    # Look for a complete SQL statement ending with semicolon
    sql_statement_pattern = r"(SELECT.*?;)"
    sql_match = re.search(sql_statement_pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if sql_match:
        text = sql_match.group(1)

    # Step 4: Remove backticks around identifiers
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Step 5: Normalize whitespace
    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)

    # Step 6: Preserve newlines for main SQL keywords to maintain readability
    keywords = [
        "SELECT",
        "FROM",
        "WHERE",
        "GROUP BY",
        "HAVING",
        "ORDER BY",
        "LIMIT",
        "JOIN",
        "LEFT JOIN",
        "RIGHT JOIN",
        "INNER JOIN",
        "OUTER JOIN",
        "UNION",
        "VALUES",
        "INSERT",
        "UPDATE",
        "DELETE",
    ]

    # Case-insensitive replacement for keywords
    pattern = "|".join(r"\b{}\b".format(k) for k in keywords)
    text = re.sub(f"({pattern})", r"\n\1", text, flags=re.IGNORECASE)

    # Step 7: Final cleanup
    # Remove leading/trailing whitespace and extra newlines
    text = text.strip()
    text = re.sub(r"\n\s*\n", "\n", text)

    return text


def validate_sql_query(query: str) -> None:
    """
    Validate that the SQL query is a read-only SELECT statement.

    Args:
        query: The SQL query to validate

    Raises:
        ValueError: If the query contains data modification commands
    """
    # Normalize query for checking (remove whitespace, convert to uppercase)
    query_upper = query.strip().upper()

    # List of forbidden SQL commands
    forbidden_commands = [
        "DELETE",
        "UPDATE",
        "INSERT",
        "DROP",
        "TRUNCATE",
        "ALTER",
        "CREATE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
        "CALL",
        "MERGE",
        "REPLACE",
    ]

    # Check if query starts with SELECT (allowing WITH clauses)
    if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
        raise ValueError(
            "Only SELECT queries are allowed. Data modification commands (INSERT, UPDATE, DELETE, etc.) are not permitted."
        )

    # Check for forbidden commands in the query
    for command in forbidden_commands:
        # Use word boundary to avoid false positives (e.g., "SELECT" containing "ELECT")
        pattern = r"\b" + re.escape(command) + r"\b"
        if re.search(pattern, query_upper):
            raise ValueError(
                f"Query contains forbidden command '{command}'. Only SELECT queries are allowed for data safety."
            )
