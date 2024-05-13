import os
from io import BytesIO
import uuid

from domain.events import DocumentCreatedEvent

from domain.directory.directory import ContainedItem, ContainedItemType

from domain.document.document import Document, KeyConcept
from domain.document.parse import DocumentProcessor

from ...firebase.persistence.repos.directory_repo import FirebaseDirectoryRepo
from ...firebase.persistence.repos.document_repo import FirebaseDocumentRepo

from ...firebase.persistence.firebase_file_storage import FirebaseFileStorage, FileMimeType
from ...openai.text_insight_extractor import OpenAITextInsightExtractor

from ...parser.docx_parser import DOCXParser
from ...parser.pdf_parser import PDFParser
from ...parser.pptx_parser import PPTXParser

from ...rabbitmq.publisher import publish_event

def allowed_file(filename: str) -> bool:
    allowed_extensions = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
    # Revisa que haya un punto en el archivo y tambien que sea un archivo permitido
    return (
        "." in filename and os.path.splitext(filename)[1].lower() in allowed_extensions
    )

from .. import celery_app

@celery_app.task # type: ignore
def create_document(creator_id: str, directory_id: str, 
                    filename: str, file_bytes: bytes):
    """ Entrypoint for the task of creating a document
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
    pll = parse_processor.from_sections(parsed_result) #type: ignore

    # Genera el insight

    text_insight_extractor = OpenAITextInsightExtractor(os.environ["OPENAI_API_KEY"])
    # Corregir esto para que sea mas eficiente
    text_insight = text_insight_extractor.extract_insight("\n".join(text.content for text in parsed_result.text_sections)) #type: ignore
    key_concepts = [
        KeyConcept(id=str(uuid.uuid1()), name=keyc, description=keyc, relationships=[])
        for keyc in text_insight.key_concepts
    ]

    # Se agrega el archivo
    url = storage.add(file, mimetype) # type: ignore

    # Se crea el UUID
    new_uuid = uuid.uuid4()

    document = Document(
        id=str(new_uuid),
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
        itemId=new_uuid,
        itemType=ContainedItemType.DOCUMENT
    )

    doc_repo.add(document)
    dir_repo.add_contained_item(directory_id, contained_item)

    publish_event(DocumentCreatedEvent(creator_id=creator_id, document_id=str(new_uuid)))
