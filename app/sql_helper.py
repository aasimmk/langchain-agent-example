from typing import Union, Dict, Any, Optional

from langchain.chains.sql_database.query import create_sql_query_chain, SQLInput, SQLInputWithTables
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.tools import QuerySQLCheckerTool, QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.language_models import BaseChatModel
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
        self.agent = create_sql_agent(llm=self.llm,
                                      toolkit=self.sql_toolkit,
                                      # extra_tools=[QuerySQLCheckerTool(db=self.db, llm=self.llm, llm_chain=)],
                                      verbose=True)

    def get_tool(self):
        return QuerySQLDataBaseTool(db=self.db)

    def generate_query_chain(
        self,
        limit: int = 0
    ) -> Runnable[Union[SQLInput, SQLInputWithTables, Dict[str, Any]], str]:
        """

        :param limit: SQL Query limit.
        :return:
        """
        return create_sql_query_chain(self.llm, self.db, k=limit)
