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
from templates import email_templates


from . import user_blueprint


@user_blueprint.route("/forgot_password", methods=["POST"])
@exclude_verify_token
def forgot_email_handle():

    author = FirebaseUserRepo()
    email_service = current_app.email_service

    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Email must be set"), 400

    email: str
    try:
        email = data["email"]

    except KeyError:
        return jsonify(msg=f"Email must be set"), 400

    try:

        reset_link = author.generate_link(email=email)
        # body_template = email_templates.RESET_PASSWORD_TEMPLATE.format(reset_link=reset_link, recipient_email = email)
        email_service.send_email(subject="Reset Password", body=str(reset_link), to_email=str(email))
        return jsonify(msg=f"Succesfully sent reset email!"), 200
    except Exception as e:
        return jsonify(msg=f"Error generating reset link: {e}"), 400
    
        