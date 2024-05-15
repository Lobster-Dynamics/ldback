from .. import celery_app
import math
import os
import uuid
from io import BytesIO
import uuid
import logging 

logger = logging.getLogger(__name__)
logging.basicConfig(filename="textbot.log", level=logging.INFO)

from domain.events import DocumentCreatedEvent

from domain.directory.directory import ContainedItem, ContainedItemType
from domain.document.document import Document, KeyConcept
from domain.document.parse import DocumentProcessor
from domain.events import DocumentCreatedEvent

from ...firebase.persistence.firebase_file_storage import (FileMimeType,
                                                           FirebaseFileStorage)
from ...firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from ...firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from ...openai.text_insight_extractor import OpenAITextInsightExtractor
from ...parser.docx_parser import DOCXParser
from ...parser.pdf_parser import PDFParser
from ...parser.pptx_parser import PPTXParser
from ...rabbitmq.publisher import publish_event
from ...vector_store.vector_store import VectorStore


def allowed_file(filename: str) -> bool:
    allowed_extensions = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
    # Revisa que haya un punto en el archivo y tambien que sea un archivo permitido
    return (
        "." in filename and os.path.splitext(
            filename)[1].lower() in allowed_extensions
    )


@celery_app.task  # type: ignore
def create_document(
    document_id: str,
    creator_id: str,
    directory_id: str,
    filename: str,
    file_bytes: bytes,
):
    """Entrypoint for the task of creating a document
    Creating a document involves the following actions:
    1- Parse the document
    2- Uploading it to persistence
    3- publishing the event
    """
    file = BytesIO(file_bytes)

    type_file = os.path.splitext(filename)[1].lower()

    # Aqui esta la magia
    storage = FirebaseFileStorage.create_from_firebase_config("documents")
    parsed_result = []
    mimetype: FileMimeType
    if type_file == ".pdf":
        mimetype = FileMimeType.PDF
        parse = PDFParser()
        parsed_result = parse.parse(file)
    elif type_file == ".doc":
        mimetype = FileMimeType.DOC
    elif type_file == ".docx":
        mimetype = FileMimeType.DOCX
        parse = DOCXParser()
        parsed_result = parse.parse(file)
    elif type_file == ".ppt":
        mimetype = FileMimeType.PPT
    elif type_file == ".pptx":
        mimetype = FileMimeType.PPTX
        parse = PPTXParser()
        parsed_result = parse.parse(file)

    # Se suben las fotos y se prepar el texto parseado

    parse_processor = DocumentProcessor()
    pll = parse_processor.from_sections(parsed_result)  # type: ignore

    # chunk pll and insert chunks into vector store
    # after that use it for insight extraction
    CHAR_CHUNK_SIZE = int(os.environ["CHAR_CHUNK_SIZE"])
    
    text_body = ""
    for text in pll.content:
        text_body += text + ""
    text_body.replace("\t", " ")
    text_body.replace("\n", " ")
    n_chunks = math.ceil(len(text_body) / CHAR_CHUNK_SIZE)
    chunks = [text_body[i*CHAR_CHUNK_SIZE:(i+1)*(CHAR_CHUNK_SIZE)] for i in range(n_chunks)]
    for chunk in chunks:
        logger.info(chunk)

    # create vector store and insert all the chunks

    vector_storage = VectorStore(
        op_api_key=os.environ["OPENAI_API_KEY"],
        pc_api_key=os.environ["PINECONE_API_KEY"],
    )
    for chunk in chunks:
        vector_storage.insert(document_id=document_id, text=chunk)

    # Genera el insight

    text_insight_extractor = OpenAITextInsightExtractor(
        os.environ["OPENAI_API_KEY"])

    # Corregir esto para que sea mas eficiente
    text_insight = text_insight_extractor.extract_insight(
        document_id, chunks, vector_storage)  # type: ignore

    key_concepts = [
        KeyConcept(id=str(uuid.uuid1()), name=keyc,
                   description=keyc, relationships=[])
        for keyc in text_insight.key_concepts
    ]

    # Se agrega el archivo
    url = storage.add(file, mimetype)  # type: ignore

    document = Document(
        id=document_id,
        ownerId=creator_id,
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

    doc_repo = FirebaseDocumentRepo()
    dir_repo = FirebaseDirectoryRepo()

    contained_item = ContainedItem(
        itemId=document_id, itemType=ContainedItemType.DOCUMENT)

    doc_repo.add(document)
    dir_repo.add_contained_item(directory_id, contained_item)

    publish_event(
        DocumentCreatedEvent(creator_id=creator_id, document_id=str(document_id))
    )
