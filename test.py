import os
import openai
import psycopg
from dotenv import load_dotenv

# Load .env file from correct path
load_dotenv(dotenv_path="mytest.env")  # or full path if needed

# Debug print
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

# Raise error if any missing
if not os.getenv("OPENAI_API_KEY") or not os.getenv("DATABASE_URL"):
    raise ValueError("Missing OPENAI_API_KEY or DATABASE_URL in your .env file")

# Proceed if no error
openai.api_key = os.getenv("OPENAI_API_KEY")
conn = psycopg.connect(os.getenv("DATABASE_URL"))
