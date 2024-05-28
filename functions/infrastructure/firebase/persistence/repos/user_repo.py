from domain.user import User
from domain.user.repo import IUserRepo
from domain.user.user import SharedItem
from firebase_admin import firestore


class FirebaseUserRepo(IUserRepo):
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("Users")

    def add(self, item: User):
        user = item.model_dump(by_alias=True)

        updated_user = dict()
        for key in user:
            updated_user[key] = str(user[key])
        doc_ref = self.collection.document(user["id"])
        doc_ref.set(updated_user)

    def get(self, id: str):
        doc_ref = self.collection.document(id)
        doc = doc_ref.get()

        if not doc.exists:
            return None

        result = doc.to_dict()
        return User(**result)

    def update(self, item: User):
        doc_ref = self.collection.document(item.id)
        doc = doc_ref.get()

        if not doc.exists:
            raise ValueError("User not found")

        try:
            user = item.model_dump(by_alias=True)
            updated_user = dict()
            for key in user:
                updated_user[key] = str(user[key])
            doc_ref.update(updated_user)
        except:
            raise ValueError("Error updating user")

    def get_with_email(self, email: str):
        docs = self.collection.where("email", "==", email).stream()
        for doc in docs:
            result = doc.to_dict()
            return User(**result)
        raise ValueError("User not found")

    def add_shared_item(self, transaction, shared_item: SharedItem, user_id: str):
        try:
            doc_ref = self.collection.document(user_id)
            shared_items_ref = doc_ref.collection("SharedItems")
            transaction.set(
                shared_items_ref.document(shared_item.type_id),
                shared_item.model_dump(by_alias=True),
            )
        except Exception as e:
            raise Exception(f"An error occurred while adding shared item {shared_item.type_id} for user {user_id}: {e}")

    def get_shared_items(self, user_id: str):
        try:
            doc_ref = self.collection.document(user_id)
            shared_items_ref = doc_ref.collection("SharedItems")
            docs = shared_items_ref.stream()
            shared_items = []
            for doc in docs:
                shared_items.append(SharedItem(**doc.to_dict()))
            return shared_items
        except Exception as e:
            raise Exception(f"An error occurred while getting shared items for user {user_id}: {e}")
