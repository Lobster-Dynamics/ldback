import os
from io import BytesIO

from flask import jsonify, request
from werkzeug.utils import secure_filename

from werkzeug.utils import secure_filename

from infrastructure.celery.tasks.create_document import create_document

from . import document_blueprint


def allowed_file(filename: str):
    allowed_extensions = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
    # Revisa que haya un punto en el archivo y tambien que sea un archivo permitido
    return (
        "." in filename and os.path.splitext(filename)[1].lower() in allowed_extensions
    )


@document_blueprint.route("/upload_document", methods=["POST"])
def upload_document_handle():
    file = request.files["file"]
    user_id = request.form["userId"]
    directory_id = request.form["directory_id"]
    if file.filename == "":
        return jsonify(msg="No selected file"), 400

    # Se saca el nombre del archivo
    filename = secure_filename(file.filename)  # type: ignore

    if not allowed_file(filename):
        return jsonify(msg="Archivo no permitido"), 400

    payload = BytesIO()
    file.save(payload)
    payload.seek(0)

    # async task    
    create_document.delay(creator_id=user_id, directory_id=directory_id, filename=filename, file_bytes=payload.getvalue()) # type: ignore
    

    return jsonify(
        {
            "msg": "File uploaded successfully",
            "userId": "",
            "url": "",
            "docId": "",
        }
    )
