import os
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
            "directory_id": os.environ["EXISTENT_DIRECTORY_ID_THAT_USER_A_HAS_NO_ACESS_TO"], 
            "name": "Should not Exist"
        })
    )
    assert res.status_code == 401

"""
When ran by itself this test screws up other tests
"""
def _test_successfuly_create_directory(
    user_a_auth_headers: dict, 
    client: FlaskClient
):
    res = client.post(
        "/directory/create_directory", 
        headers=user_a_auth_headers,
        content_type="application/json",
        data=json.dumps({
            "directory_id": os.environ["TESTING_USER_A_ROOT_DIRECTORY_ID"], 
            "name": "Should Exist"
        })
    )
    assert res.status_code == 200

