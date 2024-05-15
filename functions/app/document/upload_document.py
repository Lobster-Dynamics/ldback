import os
import uuid
from io import BytesIO

from flask import jsonify, request
from infrastructure.celery.tasks.create_document import create_document
from werkzeug.utils import secure_filename

from . import document_blueprint


def allowed_file(filename: str):
    allowed_extensions = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
    # Check if there is a dot in the filename and if it's an allowed file type
    return (
        "." in filename and os.path.splitext(
            filename)[1].lower() in allowed_extensions
    )


@document_blueprint.route("/upload_document", methods=["POST"])
def upload_document_handle():
    try:
        file = request.files["file"]
        user_id = request.form["userId"]
        directory_id = request.form["directory_id"]
        document_id = str(uuid.uuid4())

        if file.filename == "":
            return jsonify(msg="No selected file"), 400

        # Secure the filename
        filename = secure_filename(file.filename)  # type: ignore

        if not allowed_file(filename):
            return jsonify(msg="Archivo no permitido"), 400

        payload = BytesIO()
        file.save(payload)
        payload.seek(0)

        # async task
        create_document.delay(
            document_id=document_id,
            creator_id=user_id,
            directory_id=directory_id,
            filename=filename,
            file_bytes=payload.getvalue(),
        )  # type: ignore

        return (
            jsonify(
                {
                    "msg": "Se ha subido el documento correctamente",
                    "userId": user_id,
                    "document_id": document_id,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify(msg=f"Ocurrio un error: {str(e)}"), 501
