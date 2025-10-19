# api/tests/test_api_search.py

from rest_framework.test import APITestCase
from django.urls import reverse

class SearchEndpointTest(APITestCase):
    def setUp(self):
        self.client = self.client_class()
        self.url = reverse("search")

    def test_search_endpoint_ok(self):
        response = self.client.post(self.url, {"query": "test"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.data)
        self.assertIn("query=test", response.data["answer"])