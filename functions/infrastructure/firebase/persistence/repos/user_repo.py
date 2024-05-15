from domain.user import User
from domain.user.repo import IUserRepo
from firebase_admin import firestore

class FirebaseUserRepo(IUserRepo):
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('Users')

    def add(self, item: User):
        user = item.model_dump(by_alias=True)
        
        updated_user= dict()
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
            updated_user= dict()
            for key in user:
                updated_user[key] = str(user[key])
            doc_ref.update(updated_user)
        except:
            raise ValueError("Error updating user")
