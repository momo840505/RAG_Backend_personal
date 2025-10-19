# api/tests/test_api_chat.py

from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

class ChatEndpointTest(APITestCase):
    def setUp(self):
        self.client = self.client_class()
        self.url = reverse("chat")

    @patch("api.views.vector_store.similarity_search")
    @patch("api.views.openai.chat.completions.create")
    def test_chat_endpoint_success(self, mock_openai, mock_search):
        #mock vector store response
        mock_search.return_value = [
            type("Doc", (), {
                "page_content": "This is example text",
                "metadata": {"urlID": "123", "row_text": "Example document"}
                })()
                ]
        #mock OpenAI response
        mock_openai.return_value = type(
            "Response",
            (),
            {"choices": [type("C", (), {"message": type("M", (), {"content": "Mock output"})()})()]}
        )()

        payload = {"query": "Show me wellbeing data"}
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.data)
        self.assertIn("rowtext", response.data)