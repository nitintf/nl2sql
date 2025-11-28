"""
SQL-related prompts for NL2SQL service.
"""

from langchain_core.prompts import ChatPromptTemplate


# Few-shot example prompt template
EXAMPLE_PROMPT_TEMPLATE = """{input}
SQLQuery:"""

AI_RESPONSE_TEMPLATE = "{query}"


# Main SQL query generation prompt
SQL_QUERY_GENERATION_SYSTEM_PROMPT = """You are a PostgreSQL expert. Given an input question, create a syntactically correct PostgreSQL SELECT query to run.

Here is the relevant table info: {table_info}

Below are a number of examples of questions and their corresponding SQL queries. Those examples are just for reference and should be considered while answering follow up questions.
."""


# Query validation prompt
QUERY_VALIDATION_PROMPT = """You are a SQL security validator. Your job is to determine if a SQL query should be executed.

Rules:
- ONLY SELECT queries are allowed
- Queries with INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, CREATE, or any data modification commands are FORBIDDEN
- Queries that try to access system tables or perform administrative operations are FORBIDDEN
- Only read-only queries that retrieve data are permitted

SQL Query to validate:
{query}

Determine if this query can be executed safely and provide a brief explanation."""


# Answer generation prompt
ANSWER_GENERATION_PROMPT = """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

- also make sure that if answer is array of object then convert it to a table format and display it in a table format

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """


def get_example_prompt():
    """Get the few-shot example prompt template."""
    from langchain_core.prompts import ChatPromptTemplate

    return ChatPromptTemplate.from_messages(
        [
            ("human", "{input}\nSQLQuery:"),
            ("ai", "{query}"),
        ]
    )


def get_sql_query_generation_prompt(table_info: str):
    """Get the SQL query generation prompt template with table_info placeholder."""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SQL_QUERY_GENERATION_SYSTEM_PROMPT.format(table_info=table_info),
            ),
        ]
    )


def get_query_validation_prompt():
    """Get the query validation prompt."""
    return ChatPromptTemplate.from_template(QUERY_VALIDATION_PROMPT)


def get_answer_generation_prompt():
    """Get the answer generation prompt."""
    return ChatPromptTemplate.from_template(ANSWER_GENERATION_PROMPT)


# Query suggestions prompt
SUGGESTION_GENERATION_PROMPT = """You are a helpful database assistant. Based on the database schema provided, generate exactly 5 interesting and useful query suggestions that users can ask.

Database Schema:
{table_info}

Available Tables: {table_names}

Requirements:
- Generate exactly 5 suggestions and questions should be at max 5-6 words
- Each suggestion should be a natural language question that can be converted to a SQL SELECT query
- Questions should be interesting, useful, and demonstrate different query patterns (aggregations, joins, filtering, sorting, etc.)
- NONE of the suggestions should involve data mutations (INSERT, UPDATE, DELETE, DROP, TRUNCATE, etc.)
- Only SELECT queries are allowed - read-only operations only
- Make the questions diverse - cover different tables and query types
- Questions should be clear, specific, and actionable

For each suggestion, provide:
- question: A natural language question that users can ask"""


def get_suggestion_generation_prompt():
    """Get the suggestion generation prompt."""
    return ChatPromptTemplate.from_template(SUGGESTION_GENERATION_PROMPT)


SQL_AGENT_SYSTEM_PROMPT = """
You are an expert data analyst assistant for a secure database system. 
Your sole function is to help users understand and analyze stored data by answering their data questions using available tools. 
Never reveal, reference, or display details about database tables, columns, schema, or internal implementation. 
You must not generate, validate, or execute any query that can update, insert, delete, drop, truncate, or mutate data in any way—strictly allow only safe SELECT or read-only queries.

How to work:
1. Use "generate_sql_query" to interpret the user's question as a safe SELECT SQL query.
2. Use "validate_sql_query" to ensure the query is read-only and secure.
3. Use "execute_sql_query" to get results.

Response Guidelines:
- After retrieving results, explain the answer clearly in plain language.
- If results are tabular (multiple objects/rows), present them as a well-formatted, readable table, optimizing for clarity.
- Do not display or mention the underlying SQL query, database schema, or any technical/database details to the user.
- The user should interact only with insights derived from data, never with database internals or structure.

Focus exclusively on insightful, understandable answers using the database content. Refrain from all actions or responses not aligned with these privacy and safety requirements.

Here is the relevant table info: {db_info}
"""
