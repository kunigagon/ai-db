from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

# Setup SQLDatabase
db = SQLDatabase.from_uri(
    f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
)

# Setup LLM
llm = Ollama(model="mistral")

# Prompt template
template = """
Given an input question, create a syntactically correct {dialect} SQL query to run.
Then look at the results of the query and return the answer.

Use the following format:
Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer"

Only use the following tables:
{table_info}

Question: {input}
"""

prompt = PromptTemplate.from_template(template)

# Chain
chain = (
    {
        "input": RunnablePassthrough(),
        "dialect": lambda _: db.dialect,
        "table_info": lambda _: db.get_table_info(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

# Ask a question
question = "Who earns more than 65000?"
response = chain.invoke(question)

print("Response:\n", response)
