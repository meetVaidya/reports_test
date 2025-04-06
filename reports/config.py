import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configuration variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROJECT_ID = os.getenv("BQ_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET_ID")
CRED_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# System prompt for LangChain agent
SYSTEM_PROMPT = """
You are a SQL expert working with a BigQuery dataset containing sales data.
The tables include information on customers, transactions, product categories, geographies, and dates.
Be precise and avoid hallucinating columns or tables. Always use correct SQL syntax for BigQuery and SQLAlchemy.
"""

# BigQuery connection string
SQLALCHEMY_URL = f"bigquery://{PROJECT_ID}/{DATASET_ID}?credentials_path={CRED_PATH}"
