import json
from langchain_openai import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase

from config import SQLALCHEMY_URL, SYSTEM_PROMPT

# Setup SQLAlchemy + LangChain
def get_database():
    return SQLDatabase.from_uri(SQLALCHEMY_URL)

def setup_agent():
    db = get_database()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type="openai-tools",
        system_message=SYSTEM_PROMPT
    )

    return agent_executor, db

# Load query repository
def load_query_repository(file_path="queries_repository.json"):
    with open(file_path, "r") as f:
        return json.load(f)
