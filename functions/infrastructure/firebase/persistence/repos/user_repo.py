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

    def add_shared_item(self, shared_item: SharedItem, user_id: str):
        doc_ref = self.collection.document(user_id)

        shared_items_ref = doc_ref.collection("SharedItems")

        shared_items_ref.document(shared_item.type_id).set(
            shared_item.model_dump(by_alias=True)
        )
