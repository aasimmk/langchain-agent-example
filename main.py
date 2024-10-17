from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.query import QueryProcessor, QueryExecutor

load_dotenv()

app = FastAPI()
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    content: str


templates = Jinja2Templates(directory="templates")


class TemplateResponse:
    pass


@app.get("/chat")
async def index(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse(
        request=request, name="item.html", context=None
    )


@app.get("/conversation")
async def conversation(question: Question):
    print(question)
    if not question.content:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    query_processor = QueryProcessor()
    return StreamingResponse(
        query_processor.ask(question=question.content),
        media_type="text/event-stream"  # "text/plain"
    )

if __name__ == "__main__":
    q = QueryExecutor()
    q.run()

    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
