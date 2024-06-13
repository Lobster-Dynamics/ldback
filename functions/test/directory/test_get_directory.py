import os

from flask.testing import FlaskClient

from ..test_pytest_shared_fixtures import *

def test_access_denied_to_directory(
    user_a_auth_headers: dict, 
    client: FlaskClient
):
    res = client.get(
        f"/directory/get_directory/{os.environ['EXISTENT_DIRECTORY_ID_THAT_USER_A_HAS_NO_ACESS_TO']}", 
        headers=user_a_auth_headers
    )
    assert res.status_code == 401

def test_successfully_get_root_directory_of_user_a(
    user_a_auth_headers: dict, 
    client: FlaskClient
):
    res = client.get(
        f"/directory/get_directory/{os.environ['TESTING_USER_A_ROOT_DIRECTORY_ID']}", 
        headers=user_a_auth_headers
    )
    assert res.status_code == 200
