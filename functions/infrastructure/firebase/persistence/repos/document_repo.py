from domain.document import Document
from domain.document.repo import IDocumentRepo
from firebase_admin import firestore
from flask import jsonify


class FirebaseDocumentRepo(IDocumentRepo):

    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("Documents")

    def add(self, item: Document):
        # Se serializa todo el documento
        full_document_dict = item.dict(by_alias=True)

        # Se especifican las colleciones dentro de documento
        fields_to_exclude_as_collections = {
            "summary",
            "keyConcepts",
            "relationships",
            "parsedLLMInput", }

        # Se remueven las colecciones
        main_document_dict = {
            key: value
            for key, value in full_document_dict.items()
            if key not in fields_to_exclude_as_collections
        }

        document_id = str(item.id)

        # Referencia al documento
        doc_ref = self.collection.document(document_id)

        # Se establece el documento principal
        doc_ref.set(main_document_dict)

        # Se maneja 'parsed_llm_input' como una colección separada, si es necesario
        if item.parsed_llm_input is not None:
            parsed_input_ref = doc_ref.collection("ParsedLLMInput").document()
            parsed_input_ref.set({"content": item.parsed_llm_input.content})
            if item.parsed_llm_input.image_sections is not None:
                for image in item.parsed_llm_input.image_sections:
                    image_ref = parsed_input_ref.collection("ImageSections").document(image.location)
                    image_ref.set({"location": image.location, "url": image.url})

        # Se maneja 'summary' como una subcolección
        if item.summary:
            summary_ref = doc_ref.collection("Summary").document()
            summary_ref.set(item.summary.dict(by_alias=True))

        # Se maneja 'key_concepts' como una subcolección
        # TO DO quitar doble insercion de KeyConcepts
        if item.key_concepts:
            concepts_ref = doc_ref.collection("KeyConcepts")
            for concept in item.key_concepts:
                concept_doc = concepts_ref.document(str(concept.id))
                concept_doc.set(concept.dict(by_alias=True))

        # Se maneja 'relationships' como una subcolección
        if item.relationships:
            relationships_ref = doc_ref.collection("Relationships")
            for relationship in item.relationships:
                relationship_doc = relationships_ref.document()
                relationship_doc.set(relationship.dict(by_alias=True))

    def get(self, id: str):
        doc_ref = self.collection.document(id)
        doc = doc_ref.get()
        if not doc.exists:
            return None

        # Se serializa todo el documento
        result = doc.to_dict()

        subcollections = ["ParsedLLMInput", "Summary", "KeyConcepts"]

        subcollections_data = {}

        for subcollection in subcollections:
            subcollection_ref = doc_ref.collection(subcollection)
            subdocs = subcollection_ref.stream()

            subcollections_data[subcollection] = {}
            subcollections_data[subcollection] = [
                subdoc.to_dict() for subdoc in subdocs
            ]

        result["parsedLLMInput"] = subcollections_data["ParsedLLMInput"][0]["content"]
        result["summary"] = subcollections_data["Summary"][0]
        result["keyConcepts"] = subcollections_data["KeyConcepts"]
        return Document(**result)

    def update(self, item: Document):
        pass
