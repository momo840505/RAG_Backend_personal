# scripts/ingest_sample.py
# Minimal PGVector ingestion using env vars (no import from backend.settings).

import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector

# ---- Config from environment (the container already has these) ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in the container environment.")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "team_7")
PG_HOST = os.getenv("PG_HOST", "pgvector-db")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "vector_db")
CONNECTION_STRING = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
COLLECTION_NAME = "state_of_union_vectors"

# ---- Embeddings & Vector store (same as API) ----
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)

store = PGVector(
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,   # LC >= 0.3 uses 'embedding_function'
    collection_name=COLLECTION_NAME,
)

# ---- Sample texts to insert ----
texts = [
    "LangChain is a framework for building LLM-powered applications.",
    "RAG (Retrieval Augmented Generation) retrieves context from a vector database and generates answers.",
    "The State of the Union is a yearly address by the U.S. President.",
]
metadatas = [
    {"source": "notes", "topic": "langchain"},
    {"source": "notes", "topic": "rag"},
    {"source": "notes", "topic": "sotu"},
]

store.add_texts(texts=texts, metadatas=metadatas)
print(f"Inserted {len(texts)} sample docs into collection '{COLLECTION_NAME}'. ✅")
