from django.core.management.base import BaseCommand
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import os
from sqlalchemy import create_engine, text

from backend.settings import OPENAI_API_KEY, EMBEDDING_MODEL

CONNECTION_STRING = "postgresql+psycopg2://postgres:team_7@localhost:5432/vector_db"
COLLECTION_NAME = "rag_vector_embeddings_table"
CSV_FILE = "/api/data/cleaned_data.csv"

class Command(BaseCommand):
    help = "Populate pgvector table from CSV (runs only once)"

    def handle(self, *args, **options):
        engine = create_engine(CONNECTION_STRING)
        with engine.connect() as conn: # just to check that 
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {COLLECTION_NAME}"))
                count = result.scalar()
                if count > 0:
                    self.stdout.write(self.style.WARNING(f"Table '{COLLECTION_NAME}' already populated ({count} rows). Skipping ingestion."))
                    return
            except Exception:
                self.stdout.write(f"Table '{COLLECTION_NAME}' does not exist yet. Creating and populating...")

        # Load CSV
        df = pd.read_csv(CSV_FILE)

        # Load embeddings
        api_key = OPENAI_API_KEY
        if not api_key:
            self.stderr.write("OPENAI_API_KEY not set. Exiting.")
            return

        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=api_key)
        # Connect to db and initalise embedding model
        db = PGVector(
            embeddings=embeddings,
            connection=CONNECTION_STRING,
            collection_name=COLLECTION_NAME
        )
        # Populate pgvector
        db.add_texts(
            texts=df["row_text"].tolist(),
            metadatas=df.to_dict(orient="records")
        )

        self.stdout.write(self.style.SUCCESS(f"Vector DB '{COLLECTION_NAME}' populated successfully with {len(df)} rows!"))
