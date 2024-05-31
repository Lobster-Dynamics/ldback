from flask import jsonify, request
from infrastructure.firebase.persistence.repos.directory_repo import \
    FirebaseDirectoryRepo
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.user_repo import \
    FirebaseUserRepo
from datetime import datetime

from . import directory_blueprint


@directory_blueprint.route("/get_directory/<string:id>", methods=["GET"])
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
    is_shared_user = (
        hasattr(directory, "shared_users")
        and directory.shared_users is not None
        and token["uid"] in directory.shared_users
    )

    if directory.owner_id != token["uid"] and not is_shared_user:
        return jsonify(msg="Not allowed to view this directory"), 401

    directory = directory.model_dump()
    owner_ids: set = {directory["owner_id"]}
    owner_name_dict: dict = {}

    def format_date(date):
        return date.strftime("%d/%m/%Y")

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
        item["upload_date"] = format_date(contained_item.upload_date)
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

    if is_shared_user:
        directory["shared"] = True
#        directory["path"] = directory["path"][1:]
        del directory["shared_users"]
    else:
        directory["shared"] = False
        del directory["shared_users"]

    if not directory:
        return jsonify(msg="An error ocurred while getting the directory"), 400

    return jsonify(directory)
