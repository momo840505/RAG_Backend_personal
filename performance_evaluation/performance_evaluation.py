import csv
import requests
import time  # ✅ import time

INPUT_FILE = "testing_QA_Pairs.csv"
API_URL = "http://127.0.0.1:8000/api/chat_parsed/"
LLM_MODELS = ["gpt-5-nano","gpt-5-mini"]
RAG_MODEL_TYPES = [ "Fast", "Balanced", "Thoughtful" ]

model_type_params = {
    "Fast": (False, False),
    "Balanced": (True, False),
    "Thoughtful": (True, True)
}
for LLM_MODEL in LLM_MODELS:
    print("Setting LLM_MODEL to:", LLM_MODEL)
    for RAG_MODEL_TYPE in RAG_MODEL_TYPES:
        print("Starting performance evaluation for model type:", RAG_MODEL_TYPE)
        results = []

        with open(INPUT_FILE, newline='', encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for _ in range(100):
                next(reader)

            for row in reader:
                query = row["query"]
                print(f"Testing query: {query}")

                try:
                    parse_query_bool, rerank_bool = model_type_params[RAG_MODEL_TYPE]

                    # ✅ Start timer
                    start_time = time.perf_counter()

                    response = requests.post(
                        "http://127.0.0.1:8000/api/chat/",
                        json={
                            "query": query,
                            "parse_query_bool": parse_query_bool,
                            "rerank_bool": rerank_bool
                        }
                    )

                    # ✅ End timer
                    end_time = time.perf_counter()
                    response_time = end_time - start_time  # in seconds

                    if response.status_code == 200:
                        answer = response.json().get("answer", "")
                        rowtext = response.json().get("rowtext", "")
                    else:
                        answer = f"Error {response.status_code}"
                        rowtext = "Error response"
                except Exception as e:
                    answer = f"Exception: {str(e)}"
                    rowtext = "Failed to get response"
                    response_time = -1  # mark as invalid
                
                output ={
                    "id": row["id"],
                    "query": query,
                    "expected_urlID": row.get("expected_urlID", ""),
                    "is_real": row.get("is_real", ""),
                    "information_level": row.get("information_level", ""),
                    "model_answer": answer,
                    "model_rowtext": rowtext,
                    "response_time": round(response_time, 3)  # ✅ keep it clean (seconds, 3dp)
                }
                results.append(output)
                print("Output:", output)

        OUTPUT_FILE = f"qa_results_{RAG_MODEL_TYPE}_{LLM_MODEL}_test.csv"
        # Write results
        with open(OUTPUT_FILE, "a", newline='', encoding="utf-8") as outfile:
            fieldnames = [
                "id", "query", "expected_urlID", "is_real",
                "information_level", "model_answer", "model_rowtext",
                "response_time"
            ]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Results written to {OUTPUT_FILE}")
