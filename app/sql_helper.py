from typing import Union, Dict, Any, Optional

from langchain.agents import create_react_agent
from langchain.chains.sql_database.query import create_sql_query_chain, SQLInput, SQLInputWithTables
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables import Runnable

from app.settings import DB_PATH


class SQLExecutor:
    """
    This class handles executing SQL queries using LangChain's SQL agent.
    """

    def __init__(self, llm, db_uri=f"sqlite:///{DB_PATH}"):
        self.db = SQLDatabase.from_uri(db_uri)
        self.llm = llm
        self.sql_toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.system_message = """You are an agent designed to interact with a SQL database.
                Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
                Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 20 results.
                You can order the results by a relevant column to return the most interesting examples in the database.
                Never query for all the columns from a specific table, only ask for the relevant columns given the question.
                You have access to tools for interacting with the database.

                Only use the given tools. Only use the information returned by the tools to construct your final answer.
                You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

                DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

                You have access to the following tables: {table_names}

                If you need to filter on a proper noun, you must ALWAYS first look up the filter value using the "search_proper_nouns" tool!
                Do not try to guess at the proper name - use this function to find similar ones.""".format(
            table_names=self.db.get_usable_table_names()
        )

    def agent(self, use_react_agent: bool = False):
        """
        # FixMe: Langchain docs are fucked, `message_modifier` arg is error out `create_react_agent()`
        https://python.langchain.com/docs/tutorials/sql_qa/#system-prompt

        """
        if use_react_agent:
            return create_react_agent(
                llm=self.llm,
                tools=self.sql_toolkit.get_tools(),
                prompt=self.system_message
            )
        else:
            return create_sql_agent(llm=self.llm,
                                    toolkit=self.sql_toolkit,
                                    verbose=True)

    def get_tool(self):
        return QuerySQLDataBaseTool(db=self.db)

    def generate_query_chain(
        self,
        limit: int = 20
    ) -> Runnable[Union[SQLInput, SQLInputWithTables, Dict[str, Any]], str]:
        """

        :param limit: SQL Query limit.
        :return:
        """
        return create_sql_query_chain(self.llm, self.db, k=limit)
