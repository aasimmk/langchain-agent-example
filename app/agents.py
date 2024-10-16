from langchain_community.utilities.sql_database import SQLDatabase

from app.settings import DB_PATH


def debug_info():
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    print(db.dialect)
    print(db.get_usable_table_names())
    print(db.table_info)
