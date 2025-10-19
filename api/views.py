# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings

# CHANGE: Use the official OpenAI v1.x client instead of the legacy module-level API.
# Rationale: openai>=1.x migrates to the `OpenAI` client; using it avoids attribute errors.
from openai import OpenAI
import openai
import os
import json
from api.models import Feedback

# Load environment variables
from backend.settings import OPENAI_API_KEY, EMBEDDING_MODEL, LLM_MODEL

# Helper functions
from api.utils import generate_prompt, format_context, parse_response, parse_query, rerank_with_llm, preprocess_text

# CHANGE: Build the PG connection string from environment variables instead of hardcoding localhost.
# Rationale:
# - Inside Docker, the DB host is the service name (e.g., 'pgvector-db'), not 'localhost'.
# - Using env vars keeps dev/prod configurable without code edits.
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "team_7")
PG_HOST = os.getenv("PG_HOST", "pgvector-db")   # default to docker service name
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "vector_db")

# PGVector connection
# CONNECTION_STRING = "postgresql+psycopg2://postgres:team_7@localhost:5432/vector_db"
CONNECTION_STRING = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
COLLECTION_NAME = "rag_vector_embeddings_table"
BASE_URL = "https://acywa.ai4wa.com/?metadataId="

# Initialize embeddings
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
vector_store = PGVector(
    embeddings=embeddings,
    connection=CONNECTION_STRING,
    collection_name=COLLECTION_NAME
)

# CHANGE: Instantiate an OpenAI client (v1.x) once and reuse.
# Rationale: avoids relying on deprecated global openai.api_key.
client = OpenAI(api_key=OPENAI_API_KEY)

@api_view(['POST'])
def chat(request):
    # Need to add to frontend sending rerank_bool and parse_query_bool
    # Step1: Receive query from user frontend
    query = request.data.get('query', '')
    if not query:
        return Response({"error": "No query provided"}, status=400)
    query_original = query
    # Step2: Ask LLM to parse query into structured fields
    parse_query_bool = request.data.get('parse_query_bool', False)
    if parse_query_bool:
        structured_query = parse_query(query)
        query = structured_query

    # Step3: Perform similarity search using structured string
    # If we want to use re ranker we make k = 20-50 
    rerank_bool = request.data.get('rerank_bool', False)
    if rerank_bool:
        k_similar = 20
    else:
        k_similar = 5
    similar_documents = vector_store.similarity_search(query, k=k_similar)

    # Step4: Reranker here to narrow down similar documents only use if specified
    if rerank_bool:
        similar_documents = rerank_with_llm(query, similar_documents, top_n=5)

    # Step5: Generate selection prompt (same as before)
    context_text = format_context(similar_documents=similar_documents)
    selection_prompt = generate_prompt(query=query, context_text=context_text)

    try:
        selection_response = openai.chat.completions.create(
            model=LLM_MODEL,
            messages=selection_prompt
        )
    except Exception as e:
        return Response({"answer": f"Error contacting OpenAI API: {str(e)}"}, status=500)

    # Step7: Parse chosen document / urlID
    chosen_doc = parse_response(selection_response, similar_documents)
    
    try:
        url_id = chosen_doc.metadata.get("urlID")
        row_text = chosen_doc.metadata.get("row_text", "")
    except Exception as e:
        print(e)
        print(selection_response.choices[0].message.content.strip())
        url_id = None
        row_text = "LLM could not find suitable document"

    if url_id:
        visualisation_link = f"{BASE_URL}{url_id}"
    else:
        return Response({"answer": "Could not find suitable visualisation or Error", "rowtext": "No suitable query"}, status=200)
    
    # Step5: Return the visualisation URL to the users frontend.
    return Response({
        "answer": f"{visualisation_link}",
        "rowtext": row_text
    })

## TESTING A NEW RAG STYLE WHERE WE USE LLM FOR QUERY PARSING BEFORE SIMILARITY MATCHING USER QUERY TO DB
@api_view(['POST'])
def chat_parsed(request):
    # Need to add to frontend sending rerank_bool and parse_query_bool
    # Step1: Receive query from user frontend
    query = request.data.get('query', '')
    if not query:
        return Response({"error": "No query provided"}, status=400)
    query_original = query
    # Simple data preprocessing.
    query = preprocess_text(query)
    
    # Step2: Ask LLM to parse query into structured fields
    parse_query_bool = request.data.get('parse_query_bool', False)
    if parse_query_bool:
        structured_query = parse_query(query)
        query = structured_query

    # Step3: Perform similarity search using structured string
    # If we want to use re ranker we make k = 20-50 
    rerank_bool = request.data.get('rerank_bool', False)
    if rerank_bool:
        k_similar = 20
    else:
        k_similar = 5
    similar_documents = vector_store.similarity_search(query, k=k_similar)

    # Step4: Reranker here to narrow down similar documents only use if specified
    if rerank_bool:
        similar_documents = rerank_with_llm(query, similar_documents, top_n=5)

    # Step5: Generate selection prompt (same as before)
    context_text = format_context(similar_documents=similar_documents)
    selection_prompt = generate_prompt(query=query, context_text=context_text)

    try:
        selection_response = openai.chat.completions.create(
            model=LLM_MODEL,
            messages=selection_prompt
        )
    except Exception as e:
        return Response({"answer": f"Error contacting OpenAI API: {str(e)}"}, status=500)

    # Step7: Parse chosen document / urlID
    chosen_doc = parse_response(selection_response, similar_documents)
    
    try:
        url_id = chosen_doc.metadata.get("urlID")
        row_text = chosen_doc.metadata.get("row_text", "")
    except Exception as e:
        print(e)
        print(selection_response.choices[0].message.content.strip())
        url_id = None
        row_text = "LLM could not find suitable document"

    if url_id:
        visualisation_link = f"{BASE_URL}{url_id}"
    else:
        return Response({"answer": "Could not find suitable visualisation or Error", "rowtext": "No suitable query"}, status=200)
    
    # Step5: Return the visualisation URL to the users frontend.
    return Response({
        "answer": f"Here is the most relevant visualisation for your query:{visualisation_link}",
        "rowtext": row_text
    })



@api_view(['POST'])
def search(request):
    # First make the simplest stub: return a fixed string to confirm that the route is connected
    q = request.data.get('query', '')
    return Response({"answer": f"search endpoint ok; query={q}"})

# --- Feedback Endpoint ---

@api_view(["POST"])
def feedback_view(request):
    query = request.data.get("query", "").strip()
    response_text = request.data.get("response", "").strip()
    feedback_type = request.data.get("feedback", "").strip()

    if not feedback_type or feedback_type not in ["like", "dislike"]:
        return Response({"error": "Invalid feedback"}, status=400)

    # Save feedback
    Feedback.objects.create(response=response_text, feedback=feedback_type)

    return Response({"status": "success"}, status=status.HTTP_201_CREATED)

feedback = feedback_view