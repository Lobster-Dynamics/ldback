from flask import jsonify
from firebase_admin import firestore
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.firebase.persistence.firebase_file_storage import FirebaseFileStorage
from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from . import document_blueprint

from infrastructure.firebase import FIREBASE_CONFIG, FIREBASE_APP

@document_blueprint.route("/rename_document/<id>/<new_name>/<type>", methods=["GET"])
def rename_document_handle(id, new_name, type):

    repo = FirebaseDocumentRepo()
    directory = FirebaseDirectoryRepo()

    # Se consigue la respuesta
    if(str(type) == "DOCUMENT"):
        try:
            document = repo.get(str(id))
            original_name = document.name
            repo.rename(id=str(id),new_name=str(new_name))
            return jsonify({"msg": f"El documento {original_name} fue renombrado a {new_name}."}), 200
        except Exception as e:
            return jsonify({"msg": f"Error renaming document {id}: {e}"}), 400
    elif(str(type) == "FOLDER"):
        try:
            
            directory.rename_directory(id=str(id),new_name=str(new_name))
            return jsonify({"msg": f"La carpta fue renombrada a {new_name}."}), 200
        except Exception as e:
            return jsonify({"msg": f"Error renaming directory {id}: {e}"}), 400
        
        



     



