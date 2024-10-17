import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.query import QueryProcessor

load_dotenv()


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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


class Question(BaseModel):
    content: str


@app.get("/conversation")
async def conversation(question: Question):
    if not question.content:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    query_processor = QueryProcessor()
    return StreamingResponse(
        query_processor.ask(question=question.content),
        media_type="text/event-stream"  # "text/plain"
    )
