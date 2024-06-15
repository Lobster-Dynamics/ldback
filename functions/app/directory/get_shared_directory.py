from flask import jsonify, request
from infrastructure.firebase.persistence.repos.directory_repo import \
    FirebaseDirectoryRepo
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.user_repo import \
    FirebaseUserRepo

from . import directory_blueprint


@directory_blueprint.route("/get_shared_directory/<string:id>", methods=["GET"])
def get_shared_directory(id: str):
    token = request.token
    if not token:
        return jsonify(msg="Token is missing"), 400

    try:

        dir_repo = FirebaseDirectoryRepo()
        doc_repo = FirebaseDocumentRepo()
        user_repo = FirebaseUserRepo()

    except Exception as e:
        return jsonify(msg=str(e)), 500
