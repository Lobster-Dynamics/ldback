from domain.user.user import SharedItem
from flask import current_app, jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.user_repo import \
    FirebaseUserRepo

from . import directory_blueprint


@directory_blueprint.route("/share_document", methods=["PUT"])
def share_document():
    token = request.token

    try:
        data = request.json
        # Conseguimos los datos que necesitamos
        document_id = data["document_id"]
        shared_email = data["user_id"]
        uuid_user = token["uid"]
        priority = data["priority"]

        # Instanciamos los repositorios
        doc_repo = FirebaseDocumentRepo()
        user_repo = FirebaseUserRepo()

        try:
            # Revisar si el usuario existe y si el directorio existe
            shared_user = user_repo.get_with_email(shared_email)
            actual_user = user_repo.get(uuid_user)
            document = doc_repo.get_reduced(document_id)
        except KeyError:
            return (
                jsonify(msg="Document id, New directory id and Item id must be set"),
                400,
            )
        except FileNotFoundError as e:
            return jsonify(msg=str(e.args[0])), 404
        except ValueError as e:
            return jsonify(msg=str(e.args[0])), 404
        except Exception as e:
            return jsonify(msg="An error occurred"), 500

        # Revisar si el documento pertenece al usuario
        if document["ownerId"] != uuid_user:
            return jsonify(msg="Document does not belong to the user"), 403

        # Si el documento existe, hay que compartir al usuario

        shared_item = SharedItem(
            privilegeLevel=priority, type="DOCUMENT", typeId=document_id
        )

        # Se añade el objeto compartido al usuario
        user_repo.add_shared_item(shared_item, shared_user["id"])

        # Se añade al documento

        doc_repo.share_document(
            document_id,
            shared_user["id"]
        )

        # Se manda un correo a la persona que se le compartio el directorio

        email_service = current_app.email_service

        email_service.send_email(
            f"{actual_user['name']} {actual_user['lastname']} te compartio un documento",
            "Se te ha compartido un documento",
            shared_email
         )


        return jsonify(msg="Shared document successfully"), 200

    except Exception as e:
        return jsonify(msg="An error occurred"), 500
