from uuid import uuid1

from flask import jsonify, request

from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from domain.directory import Directory

from . import directory_blueprint


@directory_blueprint.route('/get_directory/<id>', methods=['POST'])
def create_directory_handle(id):
    token = request.token

    # Reference directory repo
    repo = FirebaseDirectoryRepo()

    directory = Directory(
        id=uuid1(),
        name="New Directory",
        ownerId=token.user_id,
        containedItems=[]
    )