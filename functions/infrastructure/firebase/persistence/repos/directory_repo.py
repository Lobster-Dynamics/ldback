from domain.directory import Directory
from domain.directory.directory import ContainedItem
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
    
    def add_contained_item(self, directory_id: str, item: ContainedItem):
        # Reference to the subcollection 'ContainedItems' in the specified directory
        doc_ref = self.collection.document(str(directory_id))
        if not doc_ref.get().exists:
            raise Exception("Directory not found")
        item_ref = doc_ref.collection("ContainedItems").document(str(item.item_id))
        
        # Add the document to the subcollection
        item_ref.set({
            "itemId": str(item.item_id),
            "itemType": item.item_type
        })

    def delete(self, root_directory_id: str, doc_id: str):

        try:
            # Validate the input
            if not root_directory_id or not doc_id:
                raise ValueError("Both root_directory_id and doc_id must be provided.")

            # Reference to the document to be deleted
            directory_ref = (
                self.collection
                    .document(root_directory_id)
                    .collection("ContainedItems")
                    .document(doc_id)
            )

            # Check if the document exists
            doc = directory_ref.get()
            if not doc.exists:
                print(f"Document {doc_id} in directory {root_directory_id} does not exist.")
                return None  # Exit early if the document doesn't exist

            # Start a batch for batch deletion
            batch = firestore.client().batch()

            # Delete the document
            batch.delete(directory_ref)  # Add to batch

            # Commit the batch to apply all deletions
            batch.commit()

            print(f"Successfully deleted document {doc_id} in directory {root_directory_id}.")

        except Exception as e:
            # Capture exceptions and print a meaningful message
            print(f"Error deleting document {doc_id} in directory {root_directory_id}: {e}")
            raise  # Re-raise the exception for further handling
    
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