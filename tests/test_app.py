import unittest
from app.main import app


class TestTaskFlow(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TaskFlow", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.json["status"], "ok")

    def test_version(self):
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        self.assertIn("version", response.json)

    def test_add_task(self):
        response = self.client.post(
            "/",
            data={"task": "Practice Docker"},
            follow_redirects=True
        )
        self.assertIn(b"Practice Docker", response.data)


if __name__ == "__main__":
    unittest.main()
