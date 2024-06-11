import json
from flask.testing import FlaskClient

from ..test_pytest_shared_fixtures import *

def test_unsuccessfuly_create_directory(
    user_a_auth_headers: dict, 
    client: FlaskClient
):
    res = client.post(
        "/directory/create_directory", 
        headers=user_a_auth_headers,
        content_type="application/json",
        data=json.dumps({
            "directory_id": "1eb23e40-d192-43f6-814e-ce6a3b74bebe", 
            "name": "Should not Exist"
        })
    )
    assert res.status_code == 401
    
def test_successfuly_create_directory(
    user_a_auth_headers: dict, 
    client: FlaskClient
):
    res = client.post(
        "/directory/create_directory", 
        headers=user_a_auth_headers,
        content_type="application/json",
        data=json.dumps({
            "directory_id": "c9b4194e-34f5-4336-bec4-bd661ce110d2", 
            "name": "Should Exist"
        })
    )
    assert res.status_code == 200

