from flask.testing import FlaskClient

from ..test_pytest_shared_fixtures import *

def test_access_denied_to_directory(
    auth_headers: dict, 
    client: FlaskClient
):
    res = client.get(
        "/directory/get_directory/1eb23e40-d192-43f6-814e-ce6a3b74bebe", 
        headers=auth_headers
    )
    assert res.status_code == 401
