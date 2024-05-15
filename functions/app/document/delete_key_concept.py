from flask import Blueprint, jsonify
from infrastructure.firebase.persistence.repos.keyconcept_repo import \
    FirebaseKeyConceptRepo

document_blueprint = Blueprint("document_blueprint", __name__)


@document_blueprint.route(
    "/delete_key_concept/<document_id>/<keyconcept_id>", methods=["DELETE"]
)
def delete_key_concept(document_id, keyconcept_id):
    try:
        repo = FirebaseKeyConceptRepo()
        repo.delete(document_id, keyconcept_id)
        return jsonify({"message": "KeyConcept deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    