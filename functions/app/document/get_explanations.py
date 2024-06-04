import json
import os
import requests
from flask import jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from domain.document.document import ExplanationFragment
from . import document_blueprint
from infrastructure.openai.open_ai_repo import OpenAIFragmentExtractor
from infrastructure.vector_store.vector_store import VectorStore

@document_blueprint.route("/get_explanations/<id>", methods=["GET"])
def get_explanations_handle(id):
    repo = FirebaseDocumentRepo()
    
    try:
        historicexp = repo.get(str(id))
        if historicexp:
            response = historicexp.historicexplanations
            if isinstance(response, list) and all(isinstance(fragment, ExplanationFragment) for fragment in response):
            # Serialize each WordCloud object in the list
                response = [fragment.model_dump() for fragment in response]
            return jsonify(response)
    except Exception as e:
        return jsonify({"msg": f"failed to get message: {e}"})