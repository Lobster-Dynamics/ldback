from flask.testing import FlaskClient

from ..test_pytest_shared_fixtures import *

def test_access_denied_to_directory(
    user_a_auth_headers: dict, 
    client: FlaskClient
):
    res = client.get(
        "/directory/get_directory/1eb23e40-d192-43f6-814e-ce6a3b74bebe", 
        headers=user_a_auth_headers
    )
    assert res.status_code == 401

def test_successfully_get_root_directory_of_user_a(
    user_a_auth_headers: dict, 
    client: FlaskClient
):
    res = client.get(
        "/directory/get_directory/c9b4194e-34f5-4336-bec4-bd661ce110d2", 
        headers=user_a_auth_headers
    )
    assert res.status_code == 200
