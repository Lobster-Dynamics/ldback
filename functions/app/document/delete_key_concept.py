from flask import Blueprint, jsonify
from infrastructure.firebase.persistence.repos.keyconcept_repo import \
    FirebaseKeyConceptRepo

from . import document_blueprint


@document_blueprint.route(
    "/delete_key_concept/<document_id>/<keyconcept_id>", methods=["DELETE"]
)
def delete_key_concept(document_id, keyconcept_id):
    try:
        repo = FirebaseKeyConceptRepo()
        repo.delete(str(document_id), str(keyconcept_id))
        return jsonify({"message": "KeyConcept deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
