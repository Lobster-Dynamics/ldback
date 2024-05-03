from domain.document import Document
from domain.document.document import ParsedLLMInput
from domain.document.repo import IDocumentRepo
from firebase_admin import firestore
from firebase_admin import storage
from flask import jsonify
from datetime import datetime, timedelta


class FirebaseDocumentRepo(IDocumentRepo):

    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("Documents")
        self.subcollections = ["ParsedLLMInput", "Summary", "KeyConcepts"]

    def get_public_url(bucket_name, file_path):

        """Generate a signed URL for public access."""
        bucket = storage.bucket(bucket_name)
        blob = bucket.blob(file_path)

        expiration_time = timedelta(seconds=86400)

        return blob.generate_signed_url(expiration=expiration_time)

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

        subcollections_data = {}

        for subcollection in self.subcollections:
            subcollection_ref = doc_ref.collection(subcollection)
            subdocs = subcollection_ref.stream()

            subcollections_data[subcollection] = {}
            subcollections_data[subcollection] = [
                subdoc.to_dict() for subdoc in subdocs
            ]
        parsed_input = subcollections_data["ParsedLLMInput"]
        for i,item in enumerate(parsed_input[0]["content"]):
            if item.startswith("gs://"):
                path_parts = item.split("gs://")[1].split("/")
                bucket_name = path_parts[0]
                file_path = "/".join(path_parts[1:])
                public_url = FirebaseDocumentRepo.get_public_url(bucket_name, file_path)
                parsed_input[0]["content"][i]=public_url 
        
        print(parsed_input[0]["content"])
                
        result["parsedLLMInput"] = ParsedLLMInput(content=parsed_input[0]["content"],image_sections=None)

        #result["summary"] = subcollections_data["Summary"][0]
        #result["keyConcepts"] = subcollections_data["KeyConcepts"]

        result["summary"] = None 
        result["keyConcepts"] = None 


        return Document(**result)
    
    def rename(self, id: str, new_name: str):
        doc_ref = self.collection.document(id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        doc_ref.update({"name": new_name})
        print(f"Document renamed succesfully: {new_name}")

    def update(self, item: Document):
        pass

    def delete(self, id: str):

        doc_ref = self.collection.document(id)
        doc = doc_ref.get()
        if not doc.exists:
            return None

        subcollections = ["ParsedLLMInput", "Summary", "KeyConcepts"]


        try:
            # Start a batch for batch deletion
            batch = firestore.client().batch()

            # Delete documents in subcollections
            for subcollection_name in subcollections:
                subcollection_ref = doc_ref.collection(subcollection_name)
                subdocs = subcollection_ref.stream()

                for subdoc in subdocs:
                    batch.delete(subdoc.reference)  # Add to batch

            # Delete the parent document
            batch.delete(doc_ref)  # Add to batch

            # Commit the batch to apply all deletions
            batch.commit()

            print(f"Successfully deleted document {id} and its subcollections.")
        except Exception as e:
            print(f"Error deleting document {id}: {e}")
            
    def get_reduced(self, id: str):
        doc_ref = self.collection.document(id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        result = doc.to_dict()
        for subcollection in self.subcollections:
            result[subcollection[0].lower() + subcollection[1:]] = None
        
        return Document(**result)

