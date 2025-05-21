import os
from dotenv import load_dotenv

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

from langchain_ollama import ChatOllama
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load env variables
load_dotenv()

# === 1. Connect to MySQL ===
db = SQLDatabase.from_uri(
    f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
)

# === 2. Create Tool ===
tools = [QuerySQLDataBaseTool(db=db)]

# === 3. Load LLM via Ollama
llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "mistral"))

# === 4. Prompt (MCP-compatible)
# prompt = ChatPromptTemplate.from_messages([
#     # ("system", "You are a helpful assistant that can answer questions by writing and running SQL."),
#     # MessagesPlaceholder(variable_name="chat_history"),
#    ("system", "You are a db crud assistant that can excute CRUD all data in database by running SQL."),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("user", "{input}"),
#     MessagesPlaceholder(variable_name="agent_scratchpad")
# ])

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a database assistant. You are allowed to perform full CRUD operations.

You will:
- Parse natural language into appropriate SQL statements
- Execute them using the provided SQL tool
- Respond with success messages or result rows as appropriate

You should not return SQL code — only execute it.

Examples:
- For SELECT: return the results
- For INSERT/UPDATE/DELETE: confirm success or affected rows

Be careful with DELETE and UPDATE: always include WHERE clauses unless explicitly told otherwise."""
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# === 5. Create Tool Calling Agent
agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# === 6. Query Loop
print("\n✅ LangChain SQL Agent Ready (using MCP + Tool Calling)")
while True:
    query = input("\nAsk (or 'exit'): ")
    if query.lower() in ['exit', 'quit']:
        break
    try:
        result = agent_executor.invoke({
            "input": query,
            "chat_history": []
        })
        print("🧠 Answer:", result["output"])
    except Exception as e:
        print("❌ Error:", e)
