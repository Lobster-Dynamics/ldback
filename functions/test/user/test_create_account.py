import json
import random

from flask.testing import FlaskClient
from ..test_pytest_shared_fixtures import *

def test_sucessfully_create_account(
    client: FlaskClient
): 
    FAKE_EMAIL = "interesanti2"
    SECURE_PASSWORD = "SuperSecurePassword123$$"
    res = client.post(
        "/user/create_account_email",
        content_type="application/json", 
        data=json.dumps({
            "email": f"{FAKE_EMAIL}@gmail.com" , 
            "password": SECURE_PASSWORD, 
            "name": "Juanjo", 
            "lastname": "Mejor profe",
        })
    )
    print(res.get_json())
    assert res.status_code == 200