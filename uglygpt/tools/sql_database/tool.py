# flake8: noqa
"""Tools for interacting with a SQL database."""
from typing import Any, Dict, Optional

from dataclasses import dataclass, field

from uglygpt.provider import LLMProvider, get_llm_provider

from uglygpt.chains import LLMChain
from uglygpt.prompts import PromptTemplate
from uglygpt.tools import BaseTool
from uglygpt.utilities.sql_database import SQLDatabase
from uglygpt.tools.sql_database.prompt import QUERY_CHECKER

@dataclass
class BaseSQLDatabaseTool:
    """Base tool for interacting with a SQL database."""
    db: SQLDatabase

@dataclass
class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name : str = "query_sql_db"
    description: str = """
    Input to this tool is a detailed and correct SQL query, output is a result from the database.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """

    def _run(
        self,
        query: str,
    ) -> str:
        """Execute the query, return the results or an error message."""
        return self.db.run_no_throw(query)

@dataclass
class InfoSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting metadata about a SQL database."""

    name:str = "schema_sql_db"
    description:str = """
    Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables.
    Be sure that the tables actually exist by calling list_tables_sql_db first!

    Example Input: "table1, table2, table3"
    """

    def _run(
        self,
        table_names: str,
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        return self.db.get_table_info_no_throw(table_names.split(", "))

@dataclass
class ListSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting tables names."""

    name:str = "list_tables_sql_db"
    description:str = "Input is an empty string, output is a comma separated list of tables in the database."

    def _run(
        self,
        tool_input: str = "",
    ) -> str:
        """Get the schema for a specific table."""
        return ", ".join(self.db.get_usable_table_names())

class QueryCheckerTool(BaseSQLDatabaseTool, BaseTool):
    """Use an LLM to check if a query is correct.
    Adapted from https://www.patterns.app/blog/2023/01/18/crunchbot-sql-analyst-gpt/"""
    def __init__(self, llm: Optional[LLMProvider] = None, llm_chain: Optional[LLMChain] = None):
        self.name = "query_checker_sql_db"
        self.description = """
        Use this tool to double check if your query is correct before executing it.
        Always use this tool before executing a query with query_sql_db!
        """
        self.template = QUERY_CHECKER
        self.llm = llm
        self.llm_chain = llm_chain
        if self.llm is None:
            self.llm = get_llm_provider()
        if self.llm_chain is None:
            self.llm_chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    template=QUERY_CHECKER, input_variables=["query", "dialect"]
                ),
            )
        if self.llm_chain.prompt.input_variables != ["query", "dialect"]:
            raise ValueError(
                "LLM chain for QueryCheckerTool must have input variables ['query', 'dialect']"
            )

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the LLM to check the query."""
        return self.llm_chain.predict(query=query, dialect=self.db.dialect)