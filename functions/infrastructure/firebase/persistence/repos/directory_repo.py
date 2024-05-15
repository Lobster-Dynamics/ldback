from domain.directory import Directory
from domain.directory.directory import ContainedItem
from domain.directory.repo import IDirectoryRepo
from firebase_admin import firestore

from uuid import uuid4, UUID

class FirebaseDirectoryRepo(IDirectoryRepo):
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('Directory')
        
    def add(self, item: Directory):
        fields_to_exclude_as_collections = {
            "containedItems",
        }

        directory = item.model_dump(by_alias=True)
        directory["id"] = str(directory["id"])

        if directory["parentId"] == None:
            fields_to_exclude_as_collections.add("parentId")
        else:
            directory["parentId"] = str(directory["parentId"])
        

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

    def rename_directory(self, id: str, new_name: str):
        try:
            if not id:
                raise ValueError("Directory id must be provided")
            
            directory_ref = self.collection.document(id)

            directory_ref.update({"name":new_name})
            print(f"Directory renamed succesfully: {new_name}")
        except Exception as e:
            print(f"Error renaming directory {id}: {e}")

    def delete_contained_item(self, directory_id: str, doc_id: str):

        try:
            # Validate the input
            if not directory_id or not doc_id:
                raise ValueError("Both directory_id and doc_id must be provided.")

            # Reference to the document to be deleted
            directory_ref = (
                self.collection
                    .document(directory_id)
                    .collection("ContainedItems")
                    .document(doc_id)
            )

            # Check if the document exists
            doc = directory_ref.get()
            if not doc.exists:
                print(f"Document {doc_id} in directory {directory_id} does not exist.")
                return None  # Exit early if the document doesn't exist

            # Start a batch for batch deletion
            batch = firestore.client().batch()

            # Delete the document
            batch.delete(directory_ref)  # Add to batch

            # Commit the batch to apply all deletions
            batch.commit()

            print(f"Successfully deleted document {doc_id} in directory {directory_id}.")

        except Exception as e:
            # Capture exceptions and print a meaningful message
            print(f"Error deleting document {doc_id} in directory {directory_id}: {e}")
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
    
    def new_uuid(self) -> uuid4:
        while True:
            root_directory_id = str(uuid4())
            if self.collection.document(root_directory_id).get().to_dict() is None: break
        return root_directory_id
    
    def get_all(self, id: str):
        query = self.collection.where("ownerId", "==", id)
        docs = query.stream()
        
        return docs
    
    def get_path(self, id: str):
        path = []

        while id:
            doc_ref = self.collection.document(str(id))
            doc = doc_ref.get()
            id = doc.to_dict().get("parentId")
            data = {"id": doc.id, "name": doc.to_dict().get("name")}
            path.append(data)
        return path[::-1]