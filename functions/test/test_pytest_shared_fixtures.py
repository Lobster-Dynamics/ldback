import os
import requests
import json 

import pytest 
from flask.testing import FlaskClient

from infrastructure.firebase import FIREBASE_CONFIG
from app import create_app

def _get_auth_headers(email: str, password: str) -> dict: 
    """ Returns headers needed to access routes that need authentication """

    payload = {
        "email": email, 
        "password": password, 
        "returnSecureToken": True
    }

    auth_response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}",
        data=payload,
    )
    auth_response = json.loads(auth_response.content)

    return {
        "Authorization": f"Bearer {auth_response['idToken']}"
    }


@pytest.fixture(scope="module")
def user_a_auth_headers() -> dict:
    return _get_auth_headers(email=os.environ["TESTING_USER_A_EMAIL"], password=os.environ["TESTING_USER_A_PASSWORD"])

@pytest.fixture(scope="module")
def client() -> FlaskClient:
    app = create_app()
    app.config.update({
        **app.config, 
        "TESTING": True
    })
    return app.test_client() 
