from flask import jsonify
import os
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.firebase.persistence.firebase_file_storage import FirebaseFileStorage
from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from infrastructure.vector_store.vector_store import VectorStore

from . import document_blueprint


@document_blueprint.route("/delete_document/<id>/<directory_id>", methods=["GET"])
def delete_document_handle(id, directory_id):

    repo = FirebaseDocumentRepo()
    storage = FirebaseFileStorage.create_from_firebase_config("documents")
    directory = FirebaseDirectoryRepo()
    image_storage = FirebaseFileStorage.create_from_firebase_config("images")
    vectorstore = VectorStore(op_api_key=os.environ["OPENAI_API_KEY"], pc_api_key=os.environ["PINECONE_API_KEY"])
    # Se consigue la respuesta
    try:
        document = repo.get(str(id))
        images = repo.get_image_ids(str(id))

        try:
            repo.delete(str(id))
        except Exception as e:
            print(f"Error deleting document {id}: {e}")
            return jsonify({"msg": f"Error deleting document {id}: {e}"}), 400
        
        try:
            directory.delete_contained_item(str(directory_id), str(id))
        except Exception as e:
            print(f"Error deleting document {id} from directory {directory_id}: {e}")
            return jsonify({"msg": f"Error deleting document {id} from directory {directory_id}: {e}"}), 400

        try:
            storage.delete(document.id_raw_doc)
        except Exception as e:
            print(f"Error deleting document {id} from storage: {e}")
            return jsonify({"msg": f"Error deleting document {id} from storage: {e}"}), 400
        
        try:
            if len(images) > 0:
                image_storage.delete_images(images)
        except Exception as e:
            print(f"Error deleting images {images} from storage: {e}")
            return jsonify({"msg": f"Error deleting images {images} from storage: {e}"}), 400
        
        try:
            vectorstore.deleteNamespace(str(id))
        except Exception as e:
            return jsonify({"msg": f"Error deleteing vector store of document {id}"}), 400

        
        
            

        return jsonify({"msg": f"El documento {id} fue borrado."}), 200
    except Exception as e:
        return jsonify({"msg": f"Error deleting document {id}: {e}"}), 400
        
        



     



