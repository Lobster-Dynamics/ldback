from flask import jsonify, request, current_app
from pydantic import ValidationError
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
import requests
import json

from app.middleware.decorators import exclude_verify_token
from infrastructure.firebase.persistence.repos.user_repo import FirebaseUserRepo
from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from domain.user import User
from domain.directory import Directory
from infrastructure.firebase import FIREBASE_CONFIG


from . import user_blueprint


@user_blueprint.route("/verify_password", methods=["POST"])
@exclude_verify_token
def verify_password_handle():
    try:
        try:
            data = request.get_json()
        except Exception:
            return jsonify(msg="Email, Token, Password, and RepeatPassword must be set"), 400

        try:
            email = data["email"]
            password = data["password"]
            token = data["token"]
            repeat_password = data["repeat-password"]
        except KeyError:
            return jsonify(msg="Email, Password, RepeatPassword, and Token must be set"), 400

        try:
            payload = {"oobCode": token}
            auth_response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={FIREBASE_CONFIG['apiKey']}",
                data=payload,
            )

            # Decode the response content and parse it as JSON
            auth_response = json.loads(auth_response.content)
        except Exception as e:
            return jsonify(msg=f"Error verifying token: {e}"), 400
        
        response_email = auth_response["email"]
        
        if (str(auth_response["email"]) != str(email)):
            return jsonify(msg=f"Email verification wrong: {str(response_email)}, {str(email)}"), 400
        
        response_request_type = str(auth_response["requestType"])
        
        if (str(auth_response["requestType"]) != "PASSWORD_RESET"):
            return jsonify(msg=f"Request type wrong: {response_request_type}"), 400

        if str(password) == str(repeat_password):

            payload_confirm = {"oobCode": token, "newPassword": repeat_password}
            auth_response_confirm = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={FIREBASE_CONFIG['apiKey']}",
                data=payload_confirm,
            )

            if auth_response_confirm.status_code != 200:
                return jsonify(msg="An error occurred while resetting password."), 400

            return jsonify(msg="Successfully reset password!")
    except Exception as e:
        return jsonify(msg="Invalid request: {e}"), 400