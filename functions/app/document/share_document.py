from domain.user.user import SharedItem
from firebase_admin import firestore
from flask import current_app, jsonify, request
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.user_repo import \
    FirebaseUserRepo
from templates.email_templates import SHARE

from . import document_blueprint

db = firestore.client()


@document_blueprint.route("/share_document", methods=["PUT"])
def share_document():
    token = request.token

    try:
        data = request.json
        # Conseguimos los datos que necesitamos
        document_id = data["document_id"]
        shared_email = data["shared_email"]
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
            return jsonify(msg="An error occurred", error=str(e.args[0])), 500

        # Revisar si el documento pertenece al usuario
        if document.owner_id != uuid_user:
            return jsonify(msg="Document does not belong to the user"), 403

        # Si el documento existe, hay que compartir al usuario

        shared_item = SharedItem(
            privilegeLevel=priority, type="DOCUMENT", typeId=document_id
        )

        try:
            with db.transaction() as transaction:
                # Se añade el objeto compartido al usuario
                user_repo.add_shared_item(transaction, shared_item, shared_user.id)
                # Se añade al documento
                doc_repo.share_document(transaction, document_id, shared_user.id)
        except ValueError as e:
            return jsonify(msg=str(e.args[0])), 404
        except Exception as e:
            return jsonify(msg=str(e.args[0])), 500

        # Se manda un correo a la persona que se le compartio el directorio
        sharer_name = f"{actual_user.name} {actual_user.lastname}"
        recipient_name = f"{shared_user.name} {shared_user.lastname}"
        shared_item_type = "documento"
        link = f"https://frida-research.web.app/documento?id={document_id}"
        subject = "Se te ha compartido un documento"

        try:
            share_html = SHARE.format(
                sharer_name=sharer_name,
                recipient_name=recipient_name,
                shared_item_type=shared_item_type,
                link=link,
                subject=subject,
            )

            email_service = current_app.email_service

            email_service.send_email(
                "Se te ha te compartio un documento!",
                share_html,
                shared_email,
            )

        except Exception as e:
            return jsonify(msg="Error mandando correo", error=str(e)), 500

        return jsonify(msg="Shared document successfully"), 200

    except Exception as e:
        return jsonify(msg="An error occurred", error=str(e)), 500
