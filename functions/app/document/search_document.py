from flask import jsonify, request
from fuzzywuzzy import fuzz

from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from infrastructure.firebase.persistence.firebase_file_storage import FirebaseFileStorage

from . import document_blueprint


@document_blueprint.route("/search_document/<name>", methods=["GET"])
def search_document_handle(name):
    token = request.token
    
    doc_repo = FirebaseDocumentRepo()
    dir_repo = FirebaseDirectoryRepo()
    docs = doc_repo.get_all(token["uid"])
    dirs = dir_repo.get_all(token["uid"])
    
    files = []
    
    for doc in docs:
        doc_dict = doc.to_dict()
        files.append({'extension': doc_dict["extension"], 'name': doc_dict["name"], 'id': doc_dict["id"]})
        
    for dir in dirs:
        dir_dict = dir.to_dict()
        files.append({'extension': None, 'name': dir_dict["name"], 'id': dir_dict["id"]})
    
    # Realizar la búsqueda difusa
    search_results = []
    for file in files:
        match_ratio = fuzz.partial_ratio(name.lower(), file['name'].lower())
        if match_ratio > 70:  # Umbral de coincidencia ajustado
            search_results.append({
                'extension': file['extension'],
                'name': file['name'],
                'id': file['id'],
                'match_ratio': match_ratio
            })
    
    # Ordenar resultados por ratio de coincidencia
    search_results = sorted(search_results, key=lambda x: x['match_ratio'], reverse=True)
    
    return jsonify(search_results)
    