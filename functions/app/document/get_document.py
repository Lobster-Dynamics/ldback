import json

from flask import jsonify
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo

from . import document_blueprint


@document_blueprint.route("/get_document/<id>", methods=["GET"])
def get_document_handle(id):
    # print("hola")
    # Se manda a llamar la clase de firebasedocumentsrepo

    repo = FirebaseDocumentRepo()

    # Se consigue la respuesta

    document = repo.get(str(id))

    if document:
        # Document found, return it with status 200
        return jsonify(document.dict()), 200
    else:
        return jsonify({"error": "Document not found"}), 400
