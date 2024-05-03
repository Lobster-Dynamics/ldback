from domain.directory import Directory
from domain.directory.repo import IDirectoryRepo
from firebase_admin import firestore
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from domain.document import Document

class FirebaseDirectoryRepo(IDirectoryRepo):
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('Directory')
        
    def add(self, item: Directory):
        pass

    def add_item(self, item: Document, root_directory_id: str, item_type: str):
        if item_type not in {"DOCUMENT", "DIRECTORY"}:
            raise ValueError("Invalid item_type. Must be 'DOCUMENT' or 'DIRECTORY'.")

        try:
            # Ensure the root_directory_id is valid
            if not root_directory_id:
                raise ValueError("root_directory_id cannot be empty.")

            # Reference to the sub-collection 'ContainedItems' in the specified document
            root_directory_ref = (
                self.collection
                    .document(root_directory_id)
                    .collection("ContainedItems")
                    .document(item.id)
            )
            
            # Add the document to the sub-collection
            root_directory_ref.set({
                "itemId": item.id,
                "itemType": item_type
            })

        except Exception as e:
            # Display the actual root_directory_id in the error message
            print(f"Error adding document to directory {root_directory_id}: {e}")
            raise  # Re-raise the exception for further handling or debugging


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