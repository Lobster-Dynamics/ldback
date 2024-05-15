import json
import requests
from flask import jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from . import document_blueprint
from infrastructure.openai.chat_answers import OpenAITextInsightExtractor

@document_blueprint.route("/get_message/", methods=["POST"])
def get_message_handle():
    bot = OpenAITextInsightExtractor()
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Request must contain id and query."), 400
    
    id:str
    query:str
    try:
        id = data["id"]
        query = data["query"]
    except Exception:
        return jsonify(msg=f"Failed to set id and query."), 401
    try:
        response = bot.extract_message(document_id=id, text=query)
        return jsonify(response.message)
    except Exception as e:
        return jsonify({"msg": f"failed to get message: {e}"})