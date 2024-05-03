from uuid import uuid1

from flask import jsonify, request

from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from domain.directory import Directory

from . import directory_blueprint


@directory_blueprint.route('/create_directory', methods=['POST'])
def create_directory_handle():
    token = request.token

    data = request.get_json()
    if not data:
        return jsonify(msg="Directory id and name must be set"), 400
    
    name: str
    directory_id: str
    try:
        name = data["name"]
        directory_id = data["directory_id"]
    except KeyError:
        return jsonify(msg="Directory id and name must be set"), 400
    
    # Reference directory repo
    repo = FirebaseDirectoryRepo()

    # Create a new entry in the directory collection
    directory = Directory(
        id=uuid1(),
        name=name,
        ownerId=token["user_id"],
        containedItems=[]
    )
    repo.add(directory)
    
    return jsonify(msg="Directory created successfully"), 200