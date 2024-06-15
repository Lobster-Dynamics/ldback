import json
import os
import requests
from flask import jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from . import document_blueprint
from infrastructure.openai.open_ai_repo import OpenAIFragmentExtractor
from infrastructure.vector_store.vector_store import VectorStore

@document_blueprint.route("/get_explanation", methods=["POST"])
def get_explanation_handle():
    bot = OpenAIFragmentExtractor(os.environ["OPENAI_API_KEY"], vector_store=VectorStore(pc_api_key=os.environ["PINECONE_API_KEY"], op_api_key=os.environ["OPENAI_API_KEY"]))
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Request must contain the id and query."), 400
    
    id:str
    query:str
    try:
        id = data["id"]
        query = data["query"]
    except Exception:
        return jsonify(msg=f"Failed to set id and query."), 401
    try:
        response = bot.extract_fragment(document_id=id, query=query)
        return jsonify({"msg" : f"{response.explanation}"})
    except Exception as e:
        return jsonify({"msg": f"failed to get message: {e}"})