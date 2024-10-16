from operator import itemgetter

from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.settings import DB_PATH


db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")


def debug_info():
    print(db.dialect)
    print(db.get_usable_table_names())
    print(db.table_info)


def ex1():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    generate_query = create_sql_query_chain(llm, db, k=0)
    query = generate_query.invoke({"question": "What are the year-over-year sales trends?"})
    print(query)
    execute_query = QuerySQLDataBaseTool(db=db)
    # result = execute_query.invoke(query)
    # print(result)

    template_format = """
    Based on user original question, auto generated SQL query and SQL query output,
    generate the response with insights as much as possible.
    Make sure response is formatted properly with the use of currency symbols and is a mix of pointer explanation and sentences.

    Question: {question}

    SQL Query: {query}

    SQL Result: {result}

    Answer:
    """
    answer_prompt = PromptTemplate.from_template(template_format)

    rephrase_answer = answer_prompt | llm | StrOutputParser()

    chain = (
        RunnablePassthrough.assign(query=generate_query).assign(
            result=itemgetter("query") | execute_query
        )
        | rephrase_answer
    )

    for chunk in chain.stream(
        {"question": "Who are our top 3 customers by sales volume?"},
    ):
        print(chunk, end="", flush=True)
