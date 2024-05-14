from flask import jsonify, request
from pydantic import ValidationError

from infrastructure.firebase.persistence.repos.user_repo import FirebaseUserRepo
from domain.user import User

from . import user_blueprint


@user_blueprint.route("/update_profile", methods=["POST"])
def update_profile_handle():
    token = request.token
    
    try:
        data = request.get_json()
    except Exception:
        return jsonify(msg=f"Name and Lastname must be set"), 400
    
    name: str
    lastname: str
    try:
        name = data["name"]
        lastname = data["lastname"]
    except KeyError:
        return jsonify(msg=f"Email, Password, Name and Lastname must be set"), 400
    
    repo = FirebaseUserRepo()
    # Validate format of name and lastname
    try:
        user = User(
            id=token["uid"],
            name=name,
            lastname=lastname,
            email=token["email"],
            rootDirectoryId=repo.get(token["uid"]).root_directory_id
        )
    except ValidationError:
        return jsonify(msg=f"Name and Lastname must be between 4 and 15 characters."), 400
    
    try:        
        repo.update(user)
    except ValueError:
        return jsonify(msg="An error occurred while updating the user"), 500
    
    return jsonify(msg="User updated successfully")