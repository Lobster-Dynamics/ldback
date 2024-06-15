"""
Tests that are shared by two or more directory routes
"""
import json 
import os

from flask.testing import FlaskClient

from domain.directory import Directory
from domain.directory.directory import ContainedItemType

from ..test_pytest_shared_fixtures import *

def test_create_directory_for_user_a_and_then_delete(
    user_a_auth_headers: dict, 
    client: FlaskClient
):
    """ 
    Takes as a precondition that the root directory of user is empty.
    """
    
    res = client.post(
        "/directory/create_directory", 
        headers=user_a_auth_headers,
        content_type="application/json",
        data=json.dumps({
            "directory_id": os.environ["TESTING_USER_A_ROOT_DIRECTORY_ID"], 
            "name": "Will Delete"
        })
    )
    
    directory_created_successfully = res.status_code == 200 
    assert directory_created_successfully

    res_root_directory_of_user_a = client.get(
        f"/directory/get_directory/{os.environ['TESTING_USER_A_ROOT_DIRECTORY_ID']}",
        headers=user_a_auth_headers
    )
    assert res_root_directory_of_user_a.status_code == 200

    dir_json = res_root_directory_of_user_a.get_json()

    assert len(dir_json["contained_items"]) == 1
    
    assert dir_json["contained_items"][0]["item_type"] == ContainedItemType.DIRECTORY.value

    id_of_just_created_directory = dir_json["contained_items"][0]["item_id"]

    res2 = client.get(
        f"/directory/get_directory/{id_of_just_created_directory}",
        headers=user_a_auth_headers
    )
    assert res2.status_code == 200 

    res_del = client.get(
        f"/directory/delete_directory/{id_of_just_created_directory}/{os.environ['TESTING_USER_A_ROOT_DIRECTORY_ID']}", 
        headers=user_a_auth_headers
    )
    assert res_del.status_code == 200
    
    not_found_res = client.get(
        f"/directory/get_directory/{id_of_just_created_directory}", 
        headers=user_a_auth_headers
    )
    assert not_found_res.status_code == 404
