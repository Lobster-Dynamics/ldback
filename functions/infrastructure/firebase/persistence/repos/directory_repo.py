from uuid import uuid4

from domain.directory import Directory
from domain.directory.directory import ContainedItem, DocumentToDelete
from domain.directory.repo import IDirectoryRepo
from domain.user.user import SharedItem
from firebase_admin import firestore
from google.cloud.firestore_v1 import DocumentSnapshot
from infrastructure.firebase.persistence.repos.document_repo import \
    FirebaseDocumentRepo


class FirebaseDirectoryRepo(IDirectoryRepo):
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("Directory")

        self.document_repo = FirebaseDocumentRepo()

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
        if not directory_id or not item:
            raise KeyError("Directory id and Item must be provided")

        # Reference to the subcollection 'ContainedItems' in the specified directory
        dir_ref = self.collection.document(str(directory_id))
        if not dir_ref.get().exists:
            raise FileNotFoundError("Directory not found")

        contained_ref = dir_ref.collection(
            "ContainedItems").document(str(item.item_id))

        # Add the document to the subcollection
        contained_ref.set({"itemId": str(item.item_id),
                          "itemType": item.item_type})

    def delete_contained_item(self, directory_id, item_id: str):
        if not directory_id or not item_id:
            raise KeyError("Directory id and Item must be provided")

        dir_ref = self.collection.document(str(directory_id))
        if not dir_ref.get().exists:
            raise FileNotFoundError("Directory not found")

        contained_ref = dir_ref.collection(
            "ContainedItems").document(str(item_id))
        if not contained_ref.get().exists:
            raise FileNotFoundError("Contained item not found")

        # Use a batch to delete the contained item
        batch = firestore.client().batch()
        batch.delete(contained_ref)
        batch.commit()

    def get_contained_item(self, directory_id, id: str):
        if not directory_id or not id:
            raise KeyError("Directory id and Item id must be provided")

        dir_ref = self.collection.document(str(directory_id))
        if not dir_ref.get().exists:
            raise FileNotFoundError("Directory not found")

        contained_ref = dir_ref.collection("ContainedItems").document(str(id))
        contained_item: DocumentSnapshot = contained_ref.get()
        if not contained_item.exists:
            raise FileNotFoundError("Contained item not found")

        result = contained_item.to_dict()
        return ContainedItem(**result)

    def rename_directory(self, id: str, new_name: str):
        try:
            if not id:
                raise ValueError("Directory id must be provided")

            directory_ref = self.collection.document(id)

            directory_ref.update({"name": new_name})
            print(f"Directory renamed succesfully: {new_name}")
        except Exception as e:
            print(f"Error renaming directory {id}: {e}")

    # def delete_contained_item(self, directory_id: str, doc_id: str):

    #     try:
    #         # Validate the input
    #         if not directory_id or not doc_id:
    #             raise ValueError("Both directory_id and doc_id must be provided.")

    #         # Reference to the document to be deleted
    #         directory_ref = (
    #             self.collection
    #                 .document(directory_id)
    #                 .collection("ContainedItems")
    #                 .document(doc_id)
    #         )

    #         # Check if the document exists
    #         doc = directory_ref.get()
    #         if not doc.exists:
    #             print(f"Document {doc_id} in directory {directory_id} does not exist.")
    #             return None  # Exit early if the document doesn't exist

    #         # Start a batch for batch deletion
    #         batch = firestore.client().batch()

    #         # Delete the document
    #         batch.delete(directory_ref)  # Add to batch

    #         # Commit the batch to apply all deletions
    #         batch.commit()

    #         print(f"Successfully deleted document {doc_id} in directory {directory_id}.")

    #     except Exception as e:
    #         # Capture exceptions and print a meaningful message
    #         print(f"Error deleting document {doc_id} in directory {directory_id}: {e}")
    #         raise  # Re-raise the exception for further handling

    def get(self, id: str):
        if not id:
            raise KeyError("Id must be provided")

        doc_ref = self.collection.document(id)
        doc = doc_ref.get()

        if not doc.exists:
            raise FileNotFoundError("Directory not found")

        result = doc.to_dict()
        # Obtain the data from the directory
        contained_items_ref = doc_ref.collection("ContainedItems")
        contained_items = contained_items_ref.stream()
        result["containedItems"] = {}
        result["containedItems"] = [item.to_dict() for item in contained_items]

        return Directory(**result)

    def get_reduced(self, id: str):
        if not id:
            raise KeyError("Directory id must be provided")

        doc_ref = self.collection.document(str(id))
        doc: DocumentSnapshot = doc_ref.get()
        if not doc.exists:
            raise FileNotFoundError("Directory not found")

        result = doc.to_dict()
        return Directory(**result)

    def update(self, item: Directory):
        fields_to_exclude = {"containedItems"}

        if not isinstance(item, Directory):
            raise TypeError("Item must be of type Directory")

        dir_ref = self.collection.document(str(item.id))
        if not dir_ref.get().exists:
            raise FileNotFoundError("Directory not found")

        directory = item.model_dump(by_alias=True)
        if directory["parentId"] == None:  # JUST IN CASE
            fields_to_exclude.add("parentId")

        updated_directory = dict()
        for key in directory:
            if key in fields_to_exclude:
                continue
            updated_directory[key] = str(directory[key])

        dir_ref.update(updated_directory)

    def new_uuid(self) -> uuid4:
        while True:
            root_directory_id = str(uuid4())
            if self.collection.document(root_directory_id).get().to_dict() is None:
                break
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

    def add_to_delete(
        self, id: str, list_docs: list[DocumentToDelete], list_dir: list[str]
    ):
        try:
            curr_dir = self.get(id)
        except FileNotFoundError as e:
            print(f"Error getting directory {id}: {e}")
            return
        list_dir.append(id)
        for element in curr_dir.contained_items:
            if element.item_type == "DIRECTORY":
                self.add_to_delete(
                    str(element.item_id), list_docs=list_docs, list_dir=list_dir
                )
            elif element.item_type == "DOCUMENT":
                list_docs.append(
                    DocumentToDelete(doc_id=str(
                        element.item_id), directory_id=id)
                )

    def delete_directory(self, id: str):
        if not id:
            raise ValueError("Directory_id must be provided.")

        # Reference to the directory document to be deleted
        directory_ref = self.collection.document(id)

        # Reference to the subcollection "ContainedItems"
        contained_items_ref = directory_ref.collection("ContainedItems")

        # Get all documents in the "ContainedItems" subcollection
        contained_items_docs = contained_items_ref.stream()

        # Delete each document in the "ContainedItems" subcollection
        for doc in contained_items_docs:
            try:
                doc.reference.delete()
                print(
                    f"Contained item {doc.id} in directory {id} successfully deleted.")
            except Exception as e:
                print(f"Error deleting contained item {doc.id} in directory {id}: {e}")

        # Delete the directory document
        try:
            directory_ref.delete()
            print(f"Directory with id {id} successfully deleted.")
        except Exception as e:
            print(f"Error deleting directory with id {id}: {e}")
            raise

    def add_shared_user(self, user_id: str, directory_id: str):
        try:
            doc_ref = self.collection.document(directory_id)
            doc_ref.update({"sharedUsers": firestore.ArrayUnion([user_id])})

            contained_items_docs = doc_ref.collection(
                "ContainedItems").stream()
            contained_items_list = list(contained_items_docs)

            if not contained_items_list:
                print(f"No contained items in directory {directory_id}")
                return

            for doc in contained_items_list:
                doc_data = doc.to_dict()
                try:
                    item_type = doc_data["itemType"]
                    item_id = doc_data["itemId"]

                    if item_type == "DOCUMENT":
                        self.document_repo.share_document(item_id, user_id)
                    elif item_type == "DIRECTORY":
                        self.add_shared_user(user_id, item_id)
                except KeyError as e:
                    print(f"Error adding user {user_id} to directory {directory_id}: Missing field {e}")
        except Exception as e:
            print(f"An error occurred while adding user {user_id} to directory {directory_id}: {e}")

    def share_directory(self, user_id: str, directory_id: str):
        try:
            self.add_shared_user(user_id, directory_id)
        except Exception as e:
            print(f"An error occurred while sharing directory {directory_id} with user {user_id}: {e}")
