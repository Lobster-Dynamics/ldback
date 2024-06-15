from flask import jsonify, request
from firebase_admin import firestore
import requests
import json

from app.middleware.decorators import exclude_verify_token
from infrastructure.firebase import FIREBASE_CONFIG

from . import user_blueprint


@user_blueprint.route("/login_email", methods=["POST"])
@exclude_verify_token
def login_email_handle():
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Email and Password must be set"), 400

    email: str
    password: str
    try:
        email = data["email"]
        password = data["password"]
    except KeyError:
        return jsonify(msg=f"Email and Password must be set"), 400

    payload = {"email": email, "password": password, "returnSecureToken": True}
    auth_response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}",
        data=payload,
    )

    if not auth_response.status_code == 200:
        return jsonify(msg=f"Incorrect Email or Password"), 401

    auth_response = json.loads(auth_response.content)
    firestore_client = firestore.client()
    users_ref = firestore_client.collection("Users")
    user_info = users_ref.document(auth_response["localId"]).get().to_dict()

    auth_info = {
        "token": auth_response["idToken"],
        "refreshToken": auth_response["refreshToken"],
        "name": user_info["name"],
        "lastname": user_info["lastname"],
        "root_directory_id": user_info["rootDirectoryId"],
    }
    return jsonify(auth_info)
