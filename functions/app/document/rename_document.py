from flask import jsonify
from firebase_admin import firestore
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.firebase.persistence.firebase_file_storage import FirebaseFileStorage
from . import document_blueprint

from infrastructure.firebase import FIREBASE_CONFIG, FIREBASE_APP

@document_blueprint.route("/rename_document/<id>/<new_name>", methods=["GET"])
def rename_document_handle(id, new_name):

    repo = FirebaseDocumentRepo()
    
    # Se consigue la respuesta
    try:
        document = repo.get(str(id))
        original_name = document.name
        repo.rename(id=str(id),new_name=str(new_name))
        return jsonify({"msg": f"El documento {original_name} fue renombardo a {new_name}."}), 200
    except Exception as e:
        return jsonify({"msg": f"Error deleting document {id}: {e}"}), 400
        
        



     



