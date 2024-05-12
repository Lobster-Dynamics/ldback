from flask import jsonify, request
import requests
import json

from app.middleware.decorators import exclude_verify_token
from infrastructure.firebase import FIREBASE_CONFIG

from . import user_blueprint


@user_blueprint.route("/refresh-token", methods=["POST"])
@exclude_verify_token
def refresh_token_handle():
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Refresh token must be set"), 400

    refresh_token: str
    try:
        refresh_token = data["refreshToken"]
    except KeyError:
        return jsonify(msg=f"Refresh token must be set"), 400
    
    payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    auth_response = requests.post(f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_CONFIG['apiKey']}", data=payload)
    
    if not auth_response.status_code == 200:
        return jsonify(msg=f"Invalid refresh token"), 401
    
    auth_response = json.loads(auth_response.content)
    
    auth_info = {
        "token": auth_response["id_token"],
        "refreshToken": auth_response["refresh_token"],
    }
    return jsonify(auth_info)