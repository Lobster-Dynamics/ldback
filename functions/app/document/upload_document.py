import os
import uuid
from io import BytesIO

from domain.document import Document
from domain.document.document import KeyConcept
from domain.document.parse import DocumentProcessor
from flask import jsonify, request
from infrastructure.firebase.persistence import FileMimeType, FirebaseFileStorage
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from werkzeug.utils import secure_filename

from infrastructure.firebase.persistence import (FileMimeType,
                                                 FirebaseFileStorage)
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo
from infrastructure.openai.text_insight_extractor import \
    OpenAITextInsightExtractor
from infrastructure.parser.docx_parser import DOCXParser
from infrastructure.parser.pdf_parser import PDFParser
from infrastructure.parser.pptx_parser import PPTXParser
from werkzeug.utils import secure_filename

from . import document_blueprint


def allowed_file(filename):
    allowed_extensions = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
    # Revisa que haya un punto en el archivo y tambien que sea un archivo permitido
    return (
        "." in filename and os.path.splitext(filename)[1].lower() in allowed_extensions
    )


@document_blueprint.route("/upload_document", methods=["POST"])
def upload_document_handle():
    file = request.files["file"]
    directory_id = request.form["directory_id"]
    user_id = request.form["userId"]
    if file.filename == "":
        return jsonify(msg="No selected file"), 400

    # Se saca el nombre del archivo
    filename = secure_filename(file.filename)  # type: ignore

    if not allowed_file(filename):
        return jsonify(msg="Archivo no permitido"), 400

    # Se saca la parte final

    type_file = os.path.splitext(filename)[1].lower()

    payload = BytesIO()
    file.save(payload)
    # Aqui esta la magia
    storage = FirebaseFileStorage.create_from_firebase_config("documents")
    parsed_result = []
    if type_file == ".pdf":
        mimetype = FileMimeType.PDF
        parse = PDFParser()
        parsed_result = parse.parse(payload)
    elif type_file == ".doc":
        mimetype = FileMimeType.DOC
    elif type_file == ".docx":
        mimetype = FileMimeType.DOCX
        parse = DOCXParser()
        parsed_result = parse.parse(payload)

    elif type_file == ".ppt":
        mimetype = FileMimeType.PPT
    elif type_file == ".pptx":
        mimetype = FileMimeType.PPTX
        parse = PPTXParser()
        parsed_result = parse.parse(payload)


    # Se suben las fotos y se prepar el texto parseado

    parse_processor = DocumentProcessor()
    pll = parse_processor.from_sections(parsed_result)

    # Genera el insight

    text_insight_extractor = OpenAITextInsightExtractor(os.environ["OPENAI_API_KEY"])
    # Corregir esto para que sea mas eficiente
    text_insight = text_insight_extractor.extract_insight("\n".join(text.content for text in parsed_result.text_sections))
    key_concepts = [
        KeyConcept(id=str(uuid.uuid1()), name=keyc, description=keyc, relationships=[])
        for keyc in text_insight.key_concepts
    ]

    # Se agrega el archivo
    url = storage.add(payload, mimetype)

    # Se crea el UUID
    new_uuid = uuid.uuid4()

    document = Document(
        id=str(new_uuid),
        ownerId=user_id,
        idRawDoc=url,
        name=filename,
        extension=type_file,
        parsedLLMInput=pll,
        usersWithAccess=[],
        biblioGraficInfo=None,  # Error, esto no funciona con docx asi que esta desactivado
        summary=text_insight.summary,
        keyConcepts=key_concepts,
        relationships=[],
    )

    repo = FirebaseDocumentRepo()
    directory = FirebaseDirectoryRepo()

    repo.add(document)

    directory.add_item(document, str(directory_id), "DOCUMENT")

    return jsonify(
        {
            "msg": "File uploaded successfully",
            "userId": user_id,
            "url": url,
            "docId": str(new_uuid),
        }
    )
