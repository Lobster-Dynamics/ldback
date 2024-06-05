import json
import os
import requests
from flask import jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from . import document_blueprint
from infrastructure.openai.chat_answers import OpenAIChatExtractor
from infrastructure.vector_store.vector_store import VectorStore
from domain.document.ichat_answers import MessageContent

@document_blueprint.route("/get_message", methods=["POST"])
def get_message_handle():
    token = request.token
    
    bot = OpenAIChatExtractor(os.environ["OPENAI_API_KEY"], vector_store=VectorStore(pc_api_key=os.environ["PINECONE_API_KEY"], op_api_key=os.environ["OPENAI_API_KEY"]))
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Request must contain both ids and query."), 400
    
    id:str
    query:str
    try:
        id = data["id"]
        query = data["query"]
    except Exception:
        return jsonify(msg=f"Failed to set id and query."), 401
    try:
        response = bot.extract_message(document_id=id, user_id = token["uid"], text=query)
        return jsonify(response.model_dump())
    except Exception as e:
        return jsonify({"msg": f"failed to get message: {e}"})