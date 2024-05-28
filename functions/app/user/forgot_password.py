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
        body_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Password</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                width: 90%;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 10px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #AC73D9;
                color: white;
                padding: 10px;
                text-align: center;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}
            .content {{
                padding: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 0.9em;
                color: #777;
            }}
            .button {{
                background-color: #AC73D9;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s;
            }}
            .button:hover {{
                background-color: #8a5cb6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Password Reset</h2>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Follow this link to reset your FridaRPE password for your account.</p>
                <a href="{reset_link}" style="font-size:14px; padding:10px 20px; letter-spacing:.25px; text-decoration:none; text-transform:none; display:inline-block; border-radius:5px; background-color:#AC73D9; color:#fff" >Reset Password</a>
                <p>If you didn't ask to reset your password, you can ignore this email.</p>
                <p>Thanks,</p>
                <p>Your FridaRPE team</p>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
        email_service.send_email(subject="Reset Password", body=body_template, to_email=str(email))
        return jsonify(msg=f"Succesfully sent reset email!"), 200
    except Exception as e:
        return jsonify(msg=f"Error generating reset link: {e}"), 400
    
        