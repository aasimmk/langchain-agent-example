from dotenv import load_dotenv
from app.query import QueryExecutor

load_dotenv()

if __name__ == "__main__":
    q = QueryExecutor()
    q.run()
