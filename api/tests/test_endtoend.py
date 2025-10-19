import requests

BASE_URL = "http://127.0.0.1:8000/api"  # 宿主机访问

def test_chat_and_feedback_end_to_end():
    payload = {
        "query": "Tell me about wellbeing data",
        "parse_query_bool": True,
        "rerank_bool": False
    }
    response = requests.post(f"{BASE_URL}/chat/", json=payload)
    print("CHAT:", response.status_code, response.text[:200])
    assert response.status_code == 200, f"Chat API failed ({response.status_code}): {response.text[:500]}"
    data = response.json()
    assert "answer" in data, f"Missing 'answer' in response: {data}"

    feedback_payload = {
        "query": payload["query"],
        "response": data["answer"],
        "feedback": "like"
    }
    feedback_response = requests.post(f"{BASE_URL}/feedback/", json=feedback_payload)
    print("FEEDBACK:", feedback_response.status_code, feedback_response.text[:200])
    assert feedback_response.status_code == 201, f"Feedback API failed ({feedback_response.status_code}): {feedback_response.text[:500]}"
