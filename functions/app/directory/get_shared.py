from flask import jsonify, request
from infrastructure.firebase.persistence.repos.directory_repo import \
    FirebaseDirectoryRepo
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.user_repo import \
    FirebaseUserRepo

from . import directory_blueprint

@directory_blueprint.route("/get_shared", methods=["GET"])
def get_shared_handle():
    token = request.token

    dir_repo = FirebaseDirectoryRepo()
    doc_repo = FirebaseDocumentRepo()
    user_repo = FirebaseUserRepo()

    try:
        uuid_user = token["uid"]

        try:
            shared_items = user_repo.get_shared_items(uuid_user)
            if not shared_items:
                return jsonify(msg="No shared items found"), 404
        except Exception as e:
            return jsonify(msg="An error occurred", error=str(e)), 500

        shared_start = {}
        contained_items = []

        for item in shared_items:
            item_sent = {}
            if item.type == "DIRECTORY":
                shared_item = dir_repo.get_reduced(str(item.type_id))
            elif item.type == "DOCUMENT":
                shared_item = doc_repo.get_reduced(str(item.type_id))

            if not shared_item:
                continue

            item_sent["item_id"] = item.type_id
            item_sent["item_type"] = item.type
            item_sent["name"] = shared_item.name
            item_sent["owner_id"] = shared_item.owner_id

            if item.type == "DOCUMENT":
                item_sent["extension"] = shared_item.extension

            user = user_repo.get(shared_item.owner_id)
            if user:
                item_sent["owner_name"] = f"{user.name} {user.lastname}"

            contained_items.append(item_sent)

        shared_start["contained_items"] = contained_items
        shared_start["name"] = "Compartidos conmigo"

        return jsonify(shared_start), 200

    except Exception as e:
        return jsonify(msg="An error occurred", error=str(e)), 500

