from domain.user import User
from domain.user.repo import IUserRepo
from firebase_admin import firestore

class FirebaseUserRepo(IUserRepo):
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('Users')

    def add(self, item: User): ...

    def get(self, id: str):
        doc_ref = self.collection.document(id)
        doc = doc_ref.get()

        if not doc.exists:
            return None

        result = doc.to_dict()
        return User(**result)
    
    def update(self, item: User): ...
