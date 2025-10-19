# Adding helper functions for views.py here to increase code readability
from datetime import datetime
import json
from openai import OpenAI
import openai
from rest_framework.response import Response
import re
# Load environment variables
from backend.settings import OPENAI_API_KEY, LLM_MODEL
# CHANGE: Instantiate an OpenAI client (v1.x) once and reuse.
# Rationale: avoids relying on deprecated global openai.api_key.
client = OpenAI(api_key=OPENAI_API_KEY)

# Simple preprocessing for queries and texts. Does not lowercase or remove punctation, because OpenAI embeddings handles these.
def preprocess_text(text: str) -> str:
    if not text:
        return ""
    
    text = text.strip()

    text = " ".join(text.split())
    
    text = re.sub(r"[^\x20-\x7E]+", " ", text)

    return text

# Creates prompt to ask chatgpt which visualisation is best based off of most similar contexts to user query.
def generate_prompt(query, context_text) -> list[dict[str,str]]:
    selection_prompt = [
            {"role": "system", "content": (
                "You are a strict assistant. Only pick from the provided documents. "
                "Reply with the number of the single document that best answers the question. "
                "If none are relevant, reply exactly: 'I don't know'."
            )},
            {"role": "user", "content": (
                f"Here are 5 possible documents:\n\n{context_text}\n\n"
                f"Here is the user question: {query}\n\n"
                "Which ONE document best answers this question? Reply with just the document number."
            )}
        ]
    return selection_prompt

# Format k retrieved documents into a readable string for the LLM prompt.
def format_context(similar_documents) -> str:
    return "\n\n".join(
        f"Document {i+1}:\nText: {doc.page_content}\nMetadata: {doc.metadata}"
        for i, doc in enumerate(similar_documents)
    )

# Parse the LLM response and extract the url_id from the chosen document.Returns url_id (str) if successful, otherwise None.
def parse_response(selection_response, similar_documents):
    try:
        selection_text = selection_response.choices[0].message.content.strip()

        if selection_text.lower().startswith("i don't know"):
            return None

        chosen_doc_num = int("".join(filter(str.isdigit, selection_text)))
        chosen_doc = similar_documents[chosen_doc_num - 1]

        
        return chosen_doc
    except Exception:
        return None

def parse_query(query):
    # Latest year in the data is the current year take 1, so now its 2024 but to future proof code we will keep it this way
    current_year = datetime.now().year
    latest_year = current_year - 1
    parsing_prompt = [
        {"role": "system", "content": (
            "You are a query parser. Convert the user query into a JSON object with exactly these fields: "
            "name, sex, zone, collectionYear, startAge, endAge. "
            "Rules: Always return valid JSON. If a field is missing, use an empty string (or 0 for startAge). "
            # If no identified name for visualisation return error...
            "If no endAge is given, use 24 as maximum. "
            "Sex can be 'FEMALE', 'MALE', or 'ALL' (default 'ALL'). "
            "Zones must be one of ['SA2','SA3','SA4','LGA','STATE','NATIONAL'], else empty string. "
            f"collectionYear must be a value between 1990 and {latest_year}. "
            "Return your output as a single string in this format: "
            "'name: <value>, sex: <value>, zone: <value>, collectionYear: <value>, startAge: <value>, endAge: <value>'. "
            "Examples: "
            "Query 1: 'Give me a visualisation for Cancer related admissions for ages 0-24.' "
            "Output 2: {name: Cancer related admissions, sex: ALL, zone: , collectionYear: , startAge: 0, endAge: 24}"
            "Query 2: Affected by alcohol only - 5 year prior moving average for males aged 15-19 in LGA 2012."
            "Output 2: {name: Affected by alcohol only - 5 year prior moving average, sex: MALE, zone: LGA, collectionyear: 2012, startAge: 15, endAge: 19}"
        )},
        {"role": "user", "content": f"Parse user query: {query}"}
    ]
    try:
        parsing_response = openai.chat.completions.create(
            model=LLM_MODEL,
            messages=parsing_prompt
        )
    except Exception as e:
        return Response({"answer": f"Error contacting OpenAI API: {str(e)}"}, status=500)
    print("Parsing response:", parsing_response.choices[0].message.content.strip())
    # Step3: Extract structured JSON from response
    parsed_query = parsing_response.choices[0].message.content.strip()
    return parsed_query

def rerank_with_llm(query, documents, top_n=5):
    doc_text = "\n\n".join(
        f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(documents)
    )

    rerank_prompt = [
        {"role": "system", "content": (
            "You are a reranker. Given a user query and candidate documents, "
            "you must rank the documents by their relevance to the query."
        )},
        {"role": "user", "content": (
            f"Query: {query}\n\n"
            f"Documents:\n{doc_text}\n\n"
            "Please reply with the document numbers sorted from most relevant to least relevant. "
            "Only return the numbers in order, separated by commas."
        )}
    ]

    response = openai.chat.completions.create(
        model=LLM_MODEL,
        messages=rerank_prompt
    )

    ranked_ids = [
        int(x.strip())-1
        for x in response.choices[0].message.content.split(",")
        if x.strip().isdigit()
    ]

    # Return top_n documents in new order
    return [documents[i] for i in ranked_ids[:top_n]]
