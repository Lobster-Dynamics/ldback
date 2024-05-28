import json
import os
import requests
from flask import jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from . import document_blueprint
from infrastructure.openai.chat_answers import OpenAIChatExtractor
from infrastructure.vector_store.vector_store import VectorStore
from domain.document.ichat_answers import MessageContent

@document_blueprint.route("/get_all_messages", methods=["POST"])
def get_all_messages_handle():
    bot = OpenAIChatExtractor(os.environ["OPENAI_API_KEY"], vector_store=VectorStore(pc_api_key=os.environ["PINECONE_API_KEY"], op_api_key=os.environ["OPENAI_API_KEY"]))
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Request must contain both ids and query."), 400
    
    id:str
    try:
        id = data["id"]
        userid = data["userid"]
    except Exception:
        return jsonify(msg=f"Failed to set id and query."), 401
    try:
        response = bot._all_messages(document_id=id, user_id = userid)
        if isinstance(response, list) and all(isinstance(message, MessageContent) for message in response):
            response = [message.model_dump() for message in response]
        return jsonify(response)
    except Exception as e:
        return jsonify({"msg": f"failed to get messages: {e}"}), 400