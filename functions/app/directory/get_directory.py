from flask import jsonify, request

from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.user_repo import FirebaseUserRepo

from . import directory_blueprint


@directory_blueprint.route('/get_directory/<string:id>', methods=['GET'])
def get_directory_handle(id: str):
    token = request.token
    
    # TODO: Return path to the directory
    # Reference to directory & document repo
    dir_repo = FirebaseDirectoryRepo()
    doc_repo = FirebaseDocumentRepo()
    user_repo = FirebaseUserRepo()
    
    # Get data from the directory
    try:
        directory = dir_repo.get(str(id))
    except FileNotFoundError as e:
        return jsonify(msg=str(e)), 404
    
    if not directory.owner_id == token["uid"]:
        return jsonify(msg="Not allowed to view this directory"), 401
    
    directory = directory.model_dump()
    owner_ids: set = {directory["owner_id"]}
    owner_name_dict: dict = {}

    # Add name and extension to the contained items
    for item in directory["contained_items"]:
        if item["item_type"] == "DIRECTORY":
            contained_item = dir_repo.get(str(item["item_id"]))
        elif item["item_type"] == "DOCUMENT":
            contained_item = doc_repo.get_reduced(str(item["item_id"]))

        try:
            if not contained_item:
                continue
        except FileNotFoundError as e:
            return jsonify(msg=str(e)), 404

        item["name"] = contained_item.name
        item["owner_id"] = contained_item.owner_id
        if item["item_type"] == "DOCUMENT":
            item["extension"] = contained_item.extension
        owner_ids.add(item["owner_id"])

    # Create a dictionary to map owner_id to owner_name
    for uid in owner_ids:
        user = user_repo.get(uid)
        if user:
            owner_name_dict[uid] = f"{user.name} {user.lastname}"

    # Match owner_id with owner_name
    for item in directory["contained_items"]:
        owner_name = owner_name_dict.get(item["owner_id"])
        if owner_name:
            item["owner_name"] = owner_name
    directory["owner_name"] = owner_name_dict[directory["owner_id"]]
    directory["path"] = dir_repo.get_path(str(directory["id"]))

    if not directory:
        return jsonify(msg="An error ocurred while getting the directory"), 400
        
    return jsonify(directory)