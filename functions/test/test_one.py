"""
import unittest

from app import create_app
from infrastructure.firebase import FIREBASE_APP


class CreateAccountTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        self.headers = {
            "Content-Type": "application/json",
        }

    def tearDown(self):
        self.app_context.pop()

    def test_ok_return(self):
        reponse = self.client.post(
            "/user/create_account", headers=self.headers, json={}
        )
        self.assertEqual(reponse.status_code, 200)
"""
