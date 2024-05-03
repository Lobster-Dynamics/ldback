from flask import jsonify

from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.firebase.persistence.firebase_file_storage import FirebaseFileStorage
from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo


from . import document_blueprint


@document_blueprint.route("/delete_document/<id>/<directory_id>", methods=["GET"])
def delete_document_handle(id, directory_id):

    repo = FirebaseDocumentRepo()
    storage = FirebaseFileStorage.create_from_firebase_config("documents")
    directory = FirebaseDirectoryRepo()
    # Se consigue la respuesta
    try:
        document = repo.get(str(id))
        repo.delete(str(id))
        directory.delete_contained_item(str(directory_id), str(id))
        storage.delete(document.id_raw_doc)

        return jsonify({"msg": f"El documento {id} fue borrado."}), 200
    except Exception as e:
        return jsonify({"msg": f"Error deleting document {id}: {e}"}), 400
        
        



     



