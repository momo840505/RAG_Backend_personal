# api/tests/test_api_feedback.py

from rest_framework.test import APITestCase
from django.urls import reverse
from api.models import Feedback

class FeedbackEndpointTest(APITestCase):
    def setUp(self):
        self.client = self.client_class()
        self.url = reverse("feedback")

    def test_feedback_like(self):
        payload = {
            "query": "show data",
            "response": "good answer",
            "feedback": "like"
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(Feedback.objects.count(), 1)

    def test_invalid_feedback_type(self):
        payload = {"feedback": "meh"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)