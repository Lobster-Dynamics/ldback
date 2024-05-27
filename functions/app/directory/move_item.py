from flask import jsonify, request
from infrastructure.firebase.persistence.repos.directory_repo import \
    FirebaseDirectoryRepo
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo

from . import directory_blueprint


@directory_blueprint.route("/move_item", methods=["PUT"])
def move_file_handle():
    token = request.token

    try:
        data = request.get_json()
    except Exception:
        return (
            jsonify(msg="Directory id, New directory id and Item id must be set"),
            400,
        )

    repo = FirebaseDirectoryRepo()
    doc_repo = FirebaseDocumentRepo()

    try:
        curr_dir = repo.get_reduced(data["directory_id"])
        new_dir = repo.get_reduced(data["new_directory_id"])
        item = repo.get_contained_item(data["directory_id"], data["item_id"])
    except KeyError as e:
        return (
            jsonify(msg="Directory id, New directory id and Item id must be set"),
            400,
        )
    except FileNotFoundError as e:
        return jsonify(msg=str(e.args[0])), 404
    except Exception as e:
        return jsonify(msg="An error occured"), 500

    # Check ownership of items to modify
    if (
        not curr_dir.owner_id == token["uid"]
        or not new_dir.owner_id == token["uid"]
        or (
            item.item_type == "DOCUMENT"
            and str(doc_repo.get_reduced(str(item.item_id)).owner_id) != token["uid"]
        )
        or (
            item.item_type == "DIRECTORY"
            and str(repo.get_reduced(str(item.item_id)).owner_id) != token["uid"]
        )
    ):
        return jsonify(msg="Not allowed to modify this item"), 401

    if curr_dir.id == new_dir.id:
        return jsonify(msg="Cannot move item to the same directory"), 400
    elif item.item_type == "DIRECTORY" and item.item_id == new_dir.id:
        return jsonify(msg="Cannot move directory to itself"), 400
    elif item.item_type == "DIRECTORY":
        item_dir = repo.get_reduced(item.item_id)
        item_dir.parent_id = new_dir.id
        try:
            repo.update(item_dir)
        except FileNotFoundError as e:
            return jsonify(msg=str(e.args[0])), 404
        except Exception as e:
            return jsonify(msg="An error occured"), 500

    repo.delete_contained_item(curr_dir.id, item.item_id)
    repo.add_contained_item(new_dir.id, item)

    return jsonify(msg="Item moved successfully"), 200
