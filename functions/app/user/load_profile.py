from flask import jsonify, request
from firebase_admin import firestore

from . import user_blueprint


@user_blueprint.route("/load_profile", methods=["GET"])
def load_profile_handle():
    token = request.token

    # Obtain user info from Firestore
    firestore_client = firestore.client()
    users_ref = firestore_client.collection("Users")
    user_info = users_ref.document(token["uid"]).get().to_dict()
    
    return {
        "email": token["email"],
        "uid": token["uid"],
        "name": user_info["name"],
        "lastname": user_info["lastname"],
        "root_directory_id":  user_info["rootDirectoryId"],
    }