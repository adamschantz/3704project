import unittest
from fastapi.testclient import TestClient

from main import app  # imports your FastAPI app

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint_ok(self):
        """Health endpoint should return 200 and {'ok': True}."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data, {"ok": True})

    def test_recommend_endpoint_returns_list(self):
        """
        /api/v1/recommend should return 200 and a JSON object
        with 'recommendations' as a list of club objects.
        """
        payload = {"interests": "engineering, robotics, community service"}
        response = self.client.post("/api/v1/recommend", json=payload)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("recommendations", data)
        self.assertIsInstance(data["recommendations"], list)

        if data["recommendations"]:
            first = data["recommendations"][0]
            self.assertIn("name", first)
            self.assertIn("shortName", first)
            self.assertIn("summary", first)
            # Don't require 'score' in case that changes

    def test_recommend_endpoint_requires_interests(self):
        """
        Missing 'interests' field should trigger FastAPI validation error (422).
        """
        response = self.client.post("/api/v1/recommend", json={})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()