from domain.keyconcepts.keyconcept import KeyConcept
from flask import jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.keyconcept_repo import \
    FirebaseKeyConceptRepo

from .. import document_blueprint


@document_blueprint.route("/add_key_concept", methods=["POST"])
def add_key_concept():
    token = request.token

    if not token:
        return jsonify(msg="Token is missing"), 400

    data = request.json
    document_id = data["document_id"]
    name = data["name"]

    uuid_user = token["uid"]

    try:

        # Conseguimos el documento

        krepo = FirebaseKeyConceptRepo()
        drepo = FirebaseDocumentRepo()

        document = drepo.get_reduced(document_id)

        # Revisar si el documento pertenece al usuario
        if document.owner_id != uuid_user:
            return jsonify(msg="Document does not belong to the user"), 403
        key_concept = KeyConcept(name=name)

        krepo.add(document_id, key_concept)

        return jsonify({"message": "KeyConcept deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
