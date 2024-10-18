import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.query import QueryProcessor

load_dotenv()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
]

app = FastAPI()
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/conversation")
async def conversation(request: Request):
    payload = await request.json()
    question = payload.get("question")

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    query_processor = QueryProcessor()
    return StreamingResponse(
        query_processor.ask(question=question, cli_mode=False),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=4000)
