import json
import os
import requests
from flask import jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from . import document_blueprint
from infrastructure.openai.chat_answers import OpenAIChatExtractor
from infrastructure.vector_store.vector_store import VectorStore

@document_blueprint.route("/get_message", methods=["POST"])
def get_message_handle():
    bot = OpenAIChatExtractor(os.environ["OPENAI_API_KEY"], vector_store=VectorStore(pc_api_key=os.environ["PINECONE_API_KEY"], op_api_key=os.environ["OPENAI_API_KEY"]))
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Request must contain id and query."), 400
    
    id:str
    query:str
    try:
        id = data["id"]
        query = data["query"]
        print(id)
        print(query)
    except Exception:
        return jsonify(msg=f"Failed to set id and query."), 401
    try:
        response = bot.extract_message(document_id=id, text=query)
        print(response)
        return jsonify({"msg" : f"{response.message}"})
    except Exception as e:
        return jsonify({"msg": f"failed to get message: {e}"})