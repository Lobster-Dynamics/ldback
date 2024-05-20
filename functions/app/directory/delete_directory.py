from flask import jsonify
import os
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.firebase.persistence.firebase_file_storage import FirebaseFileStorage
from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from infrastructure.vector_store.vector_store import VectorStore
from domain.directory.directory import DocumentToDelete

from . import directory_blueprint


@directory_blueprint.route("/delete_directory/<id>/<root_id>", methods=["GET"])
def delete_directory_handle(id, root_id):

    repo = FirebaseDocumentRepo()
    storage = FirebaseFileStorage.create_from_firebase_config("documents")
    directory = FirebaseDirectoryRepo()
    image_storage = FirebaseFileStorage.create_from_firebase_config("images")
    vectorstore = VectorStore(op_api_key=os.environ["OPENAI_API_KEY"], pc_api_key=os.environ["PINECONE_API_KEY"])

    documentsfordeletion = []
    directoriesfordeletion = []
    directory.add_to_delete(id, documentsfordeletion, directoriesfordeletion)

    
    
    # Se consigue la respuesta
    try:
        for doc in documentsfordeletion:
             
            document = repo.get(str(doc.doc_id))
            images = repo.get_image_ids(str(doc.doc_id))

            try:
                repo.delete(str(doc.doc_id))
            except Exception as e:
                print(f"Error deleting document {doc.doc_id}: {e}")
                return jsonify({"msg": f"Error deleting document {doc.doc_id}: {e}"}), 400
            
            try:
                directory.delete_contained_item(str(doc.directory_id), str(doc.doc_id))
            except Exception as e:
                print(f"Error deleting document {doc.doc_id} from directory {doc.directory_id}: {e}")
                return jsonify({"msg": f"Error deleting document {doc.doc_id} from directory {doc.directory_id}: {e}"}), 400

            try:
                storage.delete(document.id_raw_doc)
            except Exception as e:
                print(f"Error deleting document {doc.doc_id} from storage: {e}")
                return jsonify({"msg": f"Error deleting document {doc.doc_id} from storage: {e}"}), 400
            
            try:
                if len(images) > 0:
                    image_storage.delete_images(images)
            except Exception as e:
                print(f"Error deleting images {images} from storage: {e}")
                return jsonify({"msg": f"Error deleting images {images} from storage: {e}"}), 400
            
            try:
                vectorstore.deleteNamespace(str(doc.doc_id))
            except Exception as e:
                return jsonify({"msg": f"Error deleteing vector store of document {doc.doc_id}"}), 400
            
        for dir in reversed(directoriesfordeletion):
            try:
                directory.delete_directory(dir)
            except Exception as e:
                return jsonify({"msg": f"Error deleting directory {dir}: {e}"}), 400
            
        try:
            directory.delete_contained_item(directory_id=root_id, doc_id=id)
        except Exception as e:
            return jsonify({"msg": f"Error deleting directory {id} from {root_id}: {e}"}), 400
        

        if isinstance(documentsfordeletion, list) and all(isinstance(doc, DocumentToDelete) for doc in documentsfordeletion):
            # Serialize each WordCloud object in the list
            documentsfordeletion = [doc.model_dump() for doc in documentsfordeletion]
            
        

        return jsonify({"msg": f"El directorio {id} fue borrado con sus elementos.", "docs" : documentsfordeletion, "dirs" : directoriesfordeletion}), 200
    except Exception as e:
        return jsonify({"msg": f"Error deleting directory {id}: {e}"}), 400
        
    