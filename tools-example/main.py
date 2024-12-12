import json
import sqlite3

from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

load_dotenv()


class DatabaseManager:
    def __init__(self, db_name="student_data.db"):
        self.db_name = db_name
        self.initialize_database()

    def initialize_database(self):
        """
        Initialize the SQLite database to store student data.

        """
        conn = sqlite3.connect(self.db_name)
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

    def store_student_data(self, name, goal, achievements):
        """
        Store student data in the database.

        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # noinspection SqlResolve
        cursor.execute("""
            INSERT INTO students (name, goal, achievements)
            VALUES (?, ?, ?)
        """, (name, goal, achievements))
        conn.commit()
        conn.close()
        return "Your information has been successfully saved!"

    def query_student_data(self):
        """
        Retrieve and display all student data from the database.

        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # noinspection SqlResolve
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


class ArgumentExtractor:
    def __init__(self, llm):
        self.llm = llm

    def extract_arguments(self, user_input):
        """
        Use LLM to extract arguments dynamically.

        """
        extraction_prompt = f"""
        Extract the following information from the text if available: name, goal, achievements.
        If any information is missing, leave it as an empty string.

        Text: "{user_input}"

        Response format (JSON):
        {{
            "name": "<name>",
            "goal": "<goal>",
            "achievements": "<achievements>"
        }}
        """
        response = self.llm.predict(extraction_prompt)
        try:
            result = json.loads(response)
            name = result.get("name", "")
            goal = result.get("goal", "")
            achievements = result.get("achievements", "")

            # ToDo: Dirty patch, need more debugging
            if name and name.startswith(("[", "'")):
                del result["name"]
            if goal and goal.startswith(("[", "'")):
                del result["goal"]
            if achievements and 'none' in achievements.lower():
                del result["achievements"]
            return result

        except json.JSONDecodeError:
            return {"name": "", "goal": "", "achievements": ""}


class StudentAssistant:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm = ChatOpenAI(temperature=0)
        self.argument_extractor = ArgumentExtractor(self.llm)
        self.partial_data = {}
        self.agent = self.initialize_agent()

    def initialize_agent(self):
        tools = [
            Tool(
                name="StoreStudentData",
                func=self.handle_store_data,
                description="Stores the student's name, goal, and achievements in the database."
            )
        ]
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, args=[], kwargs={})
        # noinspection PyTypeChecker
        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent="chat-conversational-react-description",
            verbose=True,
            memory=memory
        )

    def handle_store_data(self, user_input):
        """
        Dynamically handle input and prompt for missing data.

        """
        print(f"Received input: {user_input}")  # Debug
        extracted_data = self.argument_extractor.extract_arguments(user_input)
        self.partial_data.update({k: v for k, v in extracted_data.items() if v})
        missing_parts = [key for key in ['name', 'goal', 'achievements'] if
                         key not in self.partial_data or not self.partial_data[key]]

        if missing_parts:
            return f"Please provide the following information: {', '.join(missing_parts).capitalize()}"

        response = self.db_manager.store_student_data(
            self.partial_data['name'],
            self.partial_data['goal'],
            self.partial_data['achievements']
        )
        self.partial_data.clear()
        return response

    def query_student_data(self):
        return self.db_manager.query_student_data()

    def run(self):
        print("Welcome to the Student Goal Tracker!")
        print("Provide information in the format: Name; Goal: [Your Goal]; Achievement: [Your Achievements]")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            elif user_input.lower() == "view data":
                print("Assistant: Retrieving student data...")
                print(self.query_student_data())
                continue
            response = self.agent.run(user_input)
            print(f"Assistant: {response}")


if __name__ == "__main__":
    assistant = StudentAssistant()
    assistant.run()
