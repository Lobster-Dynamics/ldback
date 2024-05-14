from flask import jsonify, request

from infrastructure.firebase.persistence.repos.user_repo import FirebaseUserRepo

from . import user_blueprint


@user_blueprint.route("/get_information", methods=["GET"])
def get_information_handle():
    token = request.token
    
    repo = FirebaseUserRepo()
    
    # Get user information
    user = repo.get(token["uid"])
    
    if not user:
        return jsonify(msg="User not found"), 404
    
    return jsonify(user.model_dump())