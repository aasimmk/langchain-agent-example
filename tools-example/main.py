import sqlite3

from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

load_dotenv()

# Temporary in-memory storage for partial data
partial_data = {}


def initialize_database():
    """
    Initialize the SQLite database to store student data.

    """
    conn = sqlite3.connect("student_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            goal TEXT,
            achievements TEXT
        )
    """)
    conn.commit()
    conn.close()


def store_student_data(name, goal, achievements):
    """
    Store student data in the database.

    """
    conn = sqlite3.connect("student_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (name, goal, achievements)
        VALUES (?, ?, ?)
    """, (name, goal, achievements))
    conn.commit()
    conn.close()
    return "Your information has been successfully saved!"


def extract_arguments_with_llm(user_input):
    """
    Use LLM to extract arguments dynamically.

    """
    prompt = f"""
    Extract the following information from the text if available: name, goal, achievements.
    If any information is missing, leave it as an empty string.

    Text: "{user_input}"

    Response format:
    Name: <name>
    Goal: <goal>
    Achievements: <achievements>
    """
    response = llm.predict(prompt)  # Corrected method call for LLM
    result = {}
    for line in response.splitlines():
        if line.startswith("Name:"):
            result["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("Goal:"):
            result["goal"] = line.split(":", 1)[1].strip()
        elif line.startswith("Achievements:"):
            result["achievements"] = line.split(":", 1)[1].strip()
    return result


def handle_store_data(user_input):
    """
    Dynamically handle input and prompt for missing data.

    """
    global partial_data
    print(f"Received input: {user_input}")  # Debugging

    extracted_data = extract_arguments_with_llm(user_input)
    partial_data.update({k: v for k, v in extracted_data.items() if v})
    missing_parts = [key for key in ['name', 'goal', 'achievements'] if
                     key not in partial_data or not partial_data[key]]

    if missing_parts:
        return f"Please provide the following information: {', '.join(missing_parts).capitalize()}"

    response = store_student_data(
        partial_data['name'],
        partial_data['goal'],
        partial_data['achievements']
    )
    partial_data.clear()  # Clear temporary storage after saving
    return response


tools = [
    Tool(
        name="StoreStudentData",
        func=handle_store_data,
        description="Stores the student's name, goal, and achievements in the database."
    )
]
llm = ChatOpenAI(temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

template = """
You are an assistant designed to collect information about students' academic goals and achievements.
Start by asking their name, then inquire about their dream job and key academic milestones. Store this information securely.
{chat_history}
"""
prompt = PromptTemplate(input_variables=["chat_history"], template=template)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="chat-conversational-react-description",
    verbose=True,
    memory=memory
)


def query_student_data():
    """Retrieve and display all student data from the database."""
    conn = sqlite3.connect("student_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, goal, achievements FROM students")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        return "\n".join(
            f"ID: {row[0]}, Name: {row[1]}, Goal: {row[2]}, Achievements: {row[3]}"
            for row in rows
        )
    else:
        return "No student data found."


def main():
    """
    Main function to run the assistant.

    """
    initialize_database()
    print("Welcome to the Student Goal Tracker!")
    print("Provide information in the format: Name; Goal: [Your Goal]; Achievement: [Your Achievements]")
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        elif user_input.lower() == "view data":
            print("Assistant: Retrieving student data...")
            print(query_student_data())
            continue
        response = agent.run(user_input)
        print(f"Assistant: {response}")


if __name__ == "__main__":
    main()
