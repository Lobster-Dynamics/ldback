from flask import jsonify, request

from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from domain.directory import Directory
from domain.directory.directory import ContainedItem

import datetime

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
    
    # Check if the directory exists and the user is the owner
    try:
        directory = repo.get(directory_id)
    except FileNotFoundError as e:
        return jsonify(msg=str(e.args[0])), 404
    
    if not directory.owner_id == token["uid"]:
        return jsonify(msg="Not allowed to modify this directory"), 401
    

    new_uuid = repo.new_uuid()

    # Create a new entry in the directory collection
    now = datetime.datetime.now()

    directory = Directory(
        id=new_uuid,
        name=name,
        ownerId=token["user_id"],
        containedItems=[],
        parentId=directory_id,
        uploadDate=now
    )
    
    contained_item = ContainedItem(
        itemId=new_uuid,
        itemType="DIRECTORY"
    )
    
    repo.add(directory)
    repo.add_contained_item(directory_id, contained_item)
    
    return jsonify(msg="Directory created successfully"), 200