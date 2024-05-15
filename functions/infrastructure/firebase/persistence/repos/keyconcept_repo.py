from abc import ABC, abstractmethod
from typing import Optional
from firebase_admin import firestore
from uuid import uuid4

from domain.keyconcepts.repo import IKeyConceptRepo
from domain.keyconcepts.keyconcept import KeyConcept


class FirebaseKeyConceptRepo(IKeyConceptRepo):
    def __init__(self):
        self.db = firestore.client()
        self.document_collection = self.db.collection('Documents')

    def add(self, document_id: str, item: KeyConcept) -> None:
        key_concept_collection = self.document_collection.document(document_id).collection('KeyConcepts')
        key_concept_doc = key_concept_collection.document(str(item.id))
        key_concept_doc.set(item.dict())

    def delete(self, document_id: str, id: str) -> None:

        key_concept_collection = self.document_collection.document(document_id).collection('KeyConcepts')
        key_concept_doc = key_concept_collection.document(id)
        key_concept_doc.delete()
    
    def get(self, id:str): ...

    def new_uuid(self) -> str:
        while True:
            key_concept_id = str(uuid4())
            if not self.db.collection('Documents').document(key_concept_id).get().exists:
                break
        return key_concept_id
