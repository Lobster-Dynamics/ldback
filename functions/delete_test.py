from firebase_admin import firestore


import json
from os import getenv

from firebase_admin import credentials, initialize_app

creds: dict
with open("./cert/frida-research-firebase-adminsdk-krmnc-3f0287837c.json", "r") as f:
    creds = json.loads(f.read())


FIREBASE_CREDENTIALS = credentials.Certificate(
    "./cert/frida-research-firebase-adminsdk-krmnc-3f0287837c.json"
)

FIREBASE_CONFIG = {
    "apiKey": getenv("API_KEY"),
    "authDomain": getenv("AUTH_DOMAIN"),
    "databaseURL": getenv("DATABASE_URL"),
    "projectId": getenv("PROJECT_ID"),
    "storageBucket": getenv("STORAGE_BUCKET"),
    "appId": getenv("APP_ID"),
}

FIREBASE_APP = initialize_app(FIREBASE_CREDENTIALS, FIREBASE_CONFIG)

db = firestore.client()
document_collection = db.collection("Documents")

key_concept_collection = document_collection.document(
    "f9e5b49e-e30f-4aff-9b07-f8d18c3c454e"
).collection("KeyConcepts")

key_concept_doc = key_concept_collection.document(
    "612ca41e-17a7-11ef-83d0-0242c0a85002"
)

key_concept_doc.delete()
