from domain.directory import Directory
from domain.directory.repo import IDirectoryRepo
from firebase_admin import firestore

class FirebaseDirectoryRepo(IDirectoryRepo):
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('Directory')
        
    def add(self, item: Directory):
        directory = item.model_dump()
        directory["id"] = str(directory["id"])

        fields_to_exclude_as_collections = {
            "containedItems",
        }

        main_directory_dict = {
            key: value
            for key, value in directory.items()
            if key not in fields_to_exclude_as_collections
        }

        doc_ref = self.collection.document(directory["id"])

        # Add the directory to the collection
        doc_ref.set(main_directory_dict)
    
    def get(self, id: str):
        doc_ref = self.collection.document(id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        result = doc.to_dict()
        # Obtain the data from the directory
        contained_items_ref = doc_ref.collection('ContainedItems')
        contained_items = contained_items_ref.stream()
        result["containedItems"] = {}
        result["containedItems"] = [item.to_dict() for item in contained_items]
        
        return Directory(**result)
    
    def update(self, item: Directory): ...