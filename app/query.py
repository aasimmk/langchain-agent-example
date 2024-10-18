import json
from operator import itemgetter

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.settings import DB_PATH
from app.sql_helper import SQLExecutor

db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")


class QueryProcessor:
    """
    This class handles user input, checks for missing parameters,
    and prompts the user for those parameters.
    """

    # noinspection PyUnusedLocal,PyArgumentList
    def __init__(self, llm_model: str = "chatgpt", model_version: str = None):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=None,
            max_retries=2,
        )
        self.sql_executor = SQLExecutor(llm=self.llm)
        self.system_template = """
        Based on user original question, auto generated SQL query and SQL query output,
        generate the response with insights as much as possible.

        Only use the given tools. Only use the information returned by the tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

        Make sure response:
        - is formatted properly with the use of currency symbols, metrics etc.
        - must contain pointer based explanation
        - must formal tone for overall answer and do not use technical words like SQL, coding, etc.

        Question: {question}

        SQL Query: {query}

        SQL Result: {result}

        Answer:
        """

    def ask(self, question: str, use_agent=False, cli_mode=True):
        """
        Method for asking the user to input a question.

        Disable the number of results per select statement to return on `create_sql_query_chain()`.

        """
        if use_agent:
            agent = self.sql_executor.agent()
            for chunk in agent.stream({"input": question}):
                if cli_mode:
                    print(chunk, end="", flush=True)
                else:
                    data = {"message": chunk}
                    data = json.dumps(data)
                    yield f"event: answer\ndata: {data}\n\n"
        else:
            print(f"Original Question >>>>>>>>>>>>>>>>> {question}")

            generate_query = self.sql_executor.generate_query_chain()
            sql_tool = self.sql_executor.get_tool()
            chain = (
                RunnablePassthrough.assign(query=generate_query).assign(
                    result=itemgetter("query") | sql_tool
                )
                | self.rephrase()
            )
            for chunk in chain.stream({"question": question}):
                if cli_mode:
                    print(chunk, end="", flush=True)
                else:
                    data = {"message": chunk}
                    data = json.dumps(data)
                    yield f"event: answer\ndata: {data}\n\n"

    def rephrase(self):
        response_prompt_template = PromptTemplate.from_template(self.system_template)
        return response_prompt_template | self.llm | StrOutputParser()

    def check_and_prompt_user(self, query: str) -> str:
        """
        # ToDo: Implement missing parameter

        Uses the LLM to check for missing parameters, prompts the user for missing data, and returns the updated query.
        """
        pass


class QueryExecutor:
    """
    Executor class that ties together the QueryProcessor and SQLExecutor to interact with the user.

    """

    def __init__(self):
        self.query_processor = QueryProcessor()

    @staticmethod
    def get_user_input() -> str:
        """
        Prompts the user to enter a query.
        """
        return input("\n\nEnter your query below: \n")

    def run(self):
        """
        Main loop that continuously accepts queries from the user and processes them.
        """
        while True:
            user_query = self.get_user_input()
            if user_query.lower() in ["exit", "quit"]:
                print("Exiting the query interface.")
                break

            self.query_processor.ask(question=user_query)
