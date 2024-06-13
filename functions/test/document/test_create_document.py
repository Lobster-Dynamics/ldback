import os
from io import BytesIO

from flask.testing import FlaskClient 
from ..test_pytest_shared_fixtures import *

def test_create_document(
    client: FlaskClient, 
    user_a_auth_headers: dict
):
    """
    Should fail as celery is not running
    """

    file = BytesIO()
    with open(f"{os.path.dirname(__file__)}/assets/pdf1.pdf", "rb") as f:
        file = BytesIO(file.read())
    file.seek(0)

    res = client.post(
        "/document/upload_document",
        headers=user_a_auth_headers,
        content_type="multipart-form", 
        data={
            "file": file, 
            "userId": os.environ["TESTING_USER_A_ID"], 
            "directory_id": os.environ["TESTING_USER_A_ROOT_DIRECTORY_ID"], 
        } 
    )

    assert res.status_code == 501