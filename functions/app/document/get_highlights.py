import json
import os
import requests
from flask import jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from . import document_blueprint
from infrastructure.openai.chat_answers import OpenAIChatExtractor
from infrastructure.vector_store.vector_store import VectorStore

@document_blueprint.route("/get_highlights", methods=["POST"])
def get_highlights_handle():
    token = request.token
    
    bot = OpenAIChatExtractor(os.environ["OPENAI_API_KEY"], vector_store=VectorStore(pc_api_key=os.environ["PINECONE_API_KEY"], op_api_key=os.environ["OPENAI_API_KEY"]))
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Request must contain both ids"), 400
    
    id:str
    try:
        id = data["id"]
    except Exception:
        return jsonify(msg=f"Failed to set id."), 401
    try:
        response = bot._highlighted_chunks(document_id=id, user_id = token["uid"])
        print(response)
        return jsonify(response)
    except Exception as e:
        return jsonify({"msg": f"failed to get text to highlight: {e}"})