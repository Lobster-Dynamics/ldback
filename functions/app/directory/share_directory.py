from domain.user.user import SharedItem
from flask import Blueprint, current_app, jsonify, request
from infrastructure.firebase.persistence.repos.directory_repo import \
    FirebaseDirectoryRepo
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.user_repo import \
    FirebaseUserRepo
from firebase_admin import firestore

from . import directory_blueprint

db = firestore.client()


@directory_blueprint.route("/share_directory", methods=["PUT"])
def share_directory_handle():
    token = request.token

    try:
        data = request.json
        # Conseguimos los datos que necesitamos
        directory_id = data["directory_id"]
        shared_email = data["shared_email"]
        uuid_user = token["uid"]
        priority = data["priority"]

        # Instanciamos el repositorio
        dir_repo = FirebaseDirectoryRepo()
        user_repo = FirebaseUserRepo()

        try:
            # Revisar si el usuario existe y si el directorio existe
            shared_user = user_repo.get_with_email(shared_email)
            actual_user = user_repo.get(uuid_user)
            directory = dir_repo.get_reduced(directory_id)
        except KeyError:
            return (
                jsonify(
                    msg="Directory id, New directory id and Item id must be set"),
                400,
            )
        except FileNotFoundError as e:
            return jsonify(msg=str(e.args[0])), 404
        except ValueError as e:
            return jsonify(msg=str(e.args[0])), 404
        except Exception as e:
            return jsonify(msg="An error occurred"), 500

        # Revisar si el directorio pertenece al usuario
        if directory.owner_id != uuid_user:
            return jsonify(msg="Directory does not belong to the user"), 403

        # Si el directorio existe, hay que compartir al usuario

        shared_item = SharedItem(
            privilegeLevel=priority, type="DIRECTORY", typeId=directory_id
        )

        # Se añade el objeto compartido al usuario

        # Se añade dentro de cada shared_item un atributo llamado shared_with

        try:
            with db.transaction() as transaction:
                dir_repo.share_directory(transaction,shared_user.id, directory_id)
                user_repo.add_shared_item(transaction,shared_item, shared_user.id)
        except ValueError as e:
            return jsonify(msg=str(e.args[0])), 404
        except Exception as e:
            return jsonify(msg=str(e.args[0])), 500


        # Se manda un correo a la persona que se le compartio el directorio

        email_service = current_app.email_service

        email_service.send_email(
            f"{actual_user.name} {actual_user.lastname} "
            "te compartio un directorio",
            "Se te ha compartido un directorio",
            shared_email,
        )

        return jsonify(msg="Directory shared successfully"), 200

    except Exception as e:
        return jsonify(status="error",msg=str(e)), 500
