
# Architecture planning
### LLM Framework:
LangChain: A framework to manage prompt construction, chain-of-thought reasoning steps, and retrieval operations.
Also, a RAG approach where the assistant uses a memory retriever to fetch relevant data from the vector DB and a structured retriever (SQL or knowledge graph queries) to fetch data from the relational DB.

### Query identifier:
Primary interaction facilitated by LLM model like GPT-4 or Claude Haiku. The LLM interprets user queries, asks clarifying questions, and generates responses.
Here, we first need to find out the intent of the query and see it the query is for fetching the student details or saving the details. This can be done via sending the query to LLM and identify the query type.

### Memory & Storage:
Memory: LangChain's memory manager can be used to storing consersation context before saving the students data. This will also make the conversation context aware.
Structured/Relational Storage: A relational database (e.g. PostgreSQL) to store student data with well-defined schemas like StudentProfile table containing marks, classification of the student’s goal, and achievements.
Also, a vector database (PG Vector) can be used to store embeddings for external knowledge like custom subject id, student id etc.

### Retrieval and Answering:
- Identify query and save the student data based on query identification, this is done agent running in a loop. Keep filling the arguments and save the data as soon as all required data is collected by the agent.
- If the request is for structured info (e.g., “What are my grades?”), the agent retrieves directly from Postgres.
- Ensures correct prompts are sent to the LLM along with retrieved data.

---

# Relevant performance metrics
## 1. Argument extraction:
The identification of query and then retrieving the arguments is crucial since a user may not supply the required data at once. So the chat system should be robust and keep prompting the user before making any updates to the Database.

## 2. Context aware chats:
The chat app should remember what is being said in the previous messages and keep filling the missing information whilst holding the relevant information in the memory.

## 3. Agent accuracy:
Ensuring that the agents reliably fetches and presents correct data is critical. If the agent misses something, it undermines the trust and usefulness.

---

## Project demo
The code demonstrates a basic example of saving/fetching student's data using memory.
The chat is based on CLI mode and keeps asking question unless the complete information is received from the user.

### Setup
- Create `.env` in the `tools-example` directory.
- Add `OPENAI_API_KEY` environment variable and put your OPENAI Key.

### Running project:
- ```python main.py```
- Type `exit` or `quit` to exit from console.

:)
