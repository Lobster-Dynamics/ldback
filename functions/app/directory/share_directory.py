from flask import Blueprint, current_app, jsonify, request
from infrastructure.firebase.persistence.repos.directory_repo import \
    FirebaseDirectoryRepo
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.user_repo import \
    FirebaseUserRepo

from . import directory_blueprint


@directory_blueprint.route("/share_directory", methods=["PUT"])
def share_directory_handle():
    token = request.token

    try:
        data = request.json()

        # Conseguimos los datos que necesitamos

        directory_id = data["directory_id"]

        shared_email = data["user_id"]

        uuid_user = token["uid"]

        # Instanciamos el repositorio
        dir_repo = FirebaseDirectoryRepo()
        doc_repo = FirebaseDocumentRepo()
        user_repo = FirebaseUserRepo()

        # Revisar si el usuario existe

        shared_user = user_repo.get_with_email(shared_email)

        if not shared_user:
            return jsonify(msg="User not found"), 404

        # Revisar si el directorio existe

        directory = dir_repo.get_reduced(directory_id)


        # Revisar si el directorio pertenece al usuario

    except Exception as e:
        return jsonify(msg=str(e)), 500
