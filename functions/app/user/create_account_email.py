from flask import jsonify, request
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


@user_blueprint.route("/create_account_email", methods=["POST"])
@exclude_verify_token
def create_account_email_handle():
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Email, Password, Name and Lastname must be set"), 400

    email: str
    password: str
    name: str
    lastname: str
    try:
        email = data["email"]
        password = data["password"]
        name = data["name"]
        lastname = data["lastname"]
    except KeyError:
        return jsonify(msg=f"Email, Password, Name and Lastname must be set"), 400

    # Reference to user & directory repo
    user_repo = FirebaseUserRepo()
    directory_repo = FirebaseDirectoryRepo()

    # Validate format of email, name and lastname
    try:
        user = User(
            id="",
            name=name,
            lastname=lastname,
            email=email,
            rootDirectoryId=directory_repo.new_uuid()
        )
        
        directory = Directory(
            id=user.root_directory_id,
            name="Mi Unidad",
            ownerId=""
        )

    except ValidationError:
        return jsonify(msg=f"Email and Lastname must be between 4 and 15 characters. Email must be valid"), 400

    try:
        # Create user in Firebase Auth
        user_info: auth.UserRecord = auth.create_user(email=email, password=password)
    except ValueError:
        return jsonify(msg=f"Invalid Email or Password"), 400
    except FirebaseError:
        return jsonify(msg=f"An error ocurred while creating the user."), 500
    
    payload = {"email": email, "password": password, "returnSecureToken": True}
    auth_response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}",
        data=payload,
    )
    
    if not auth_response.status_code == 200:
        return jsonify(msg=f"An error ocurred while creating the user."), 400
    
    auth_response = json.loads(auth_response.content)
    
    user.id = user_info.uid
    directory.owner_id = user_info.uid
    user_repo.add(user)
    directory_repo.add(directory)

    auth_info = {
        "token": auth_response["idToken"],
        "refreshToken": auth_response["refreshToken"],
        "name": name,
        "lastname": lastname,
        "root_directory_id": str(directory.id)
    }
    return jsonify(auth_info)
    