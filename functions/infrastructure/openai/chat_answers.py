import json
from typing import List

from openai import OpenAI
from domain.document.ivector_store import IVectorStore, ResultingChunk
from domain.document.ichat_answers import IChatAnswers
from domain.document.ichat_answers import MessageContent
from infrastructure.vector_store.vector_store import VectorStore
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter


import uuid
import datetime


class OpenAIChatExtractor(IChatAnswers):
    def __init__(self, api_key: str, vector_store: IVectorStore):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
        self._vector_store = vector_store
        self.db = firestore.client()

    def _past_messages(self, document_id: str, user_id: str, amount: int) -> List[MessageContent]:
        doc_ref = self.db.collection("Documents").document(document_id).collection("PastMessages")
        query = doc_ref.where(filter=FieldFilter("userID", "==", user_id)).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(amount)
        results = query.stream()
        messages = []
        for result in results:
            res = result.to_dict()
            messages.append(MessageContent(message=res["content"], mes_id=res["id"], role=res["role"]))
        return messages
    
    def _highlighted_chunks(self, document_id: str, user_id: str, message_id: str) -> List[ResultingChunk]:
        vector_store = self._vector_store
        query = self.db.collection("Documents").document(document_id).collection("PastMessages").document(message_id)
        result = query.get()
        message = result.to_dict()
        chunks = vector_store.get_similar_chunks(document_id, 3, str(message["content"]))
        return chunks
            

    def _all_messages(self, document_id: str, user_id: str) -> List[MessageContent]:
        doc_ref = self.db.collection("Documents").document(document_id).collection("PastMessages")
        query = doc_ref.where(filter=FieldFilter("userID", "==", user_id)).order_by("timestamp", direction=firestore.Query.DESCENDING)
        result = query.stream()
        reversed_message = []
        for message in result: 
            res = message.to_dict()
            reversed_message.append(MessageContent(message=res["content"],mes_id=res["id"], role=res["role"]))
            
        reversed_message = reversed_message[::-1]

        
        return reversed_message



    def _message_completion(self, document_id: str, user_id: str, text: str, vector_store: IVectorStore) -> MessageContent:
        chunks = vector_store.get_similar_chunks(document_id, 3, text)
        text_block = "\n".join([chunk.text for chunk in chunks])
        message_id = str(uuid.uuid1())
        response_id = str(uuid.uuid1())

        past_messages=self._past_messages(document_id, user_id, 10)
        text_past_messages = "\n".join([past_message.message for past_message in past_messages])

        now = datetime.datetime.now()
        doc_ref = self.db.collection("Documents").document(document_id).collection("PastMessages").document(message_id)
        doc_ref.set({"id": message_id, "content": text, "userID": user_id, "role": "user", "documentID": document_id, "timestamp": now})

        #Deprecable si le echamos coco, era para historial con busqueda semantica, actualmente es para almacenar el mensaje embeddeado
        #messages = vector_store.get_similar_past_messages(document_id, 3, text)
        #text_messages = "\n".join([f"{msg.question}: {msg.answer}" for msg in messages])
        
        whole_prompt = f"""
        You are an expert assistant chatbot having a conversation with a user. Your role is to examine the provided texts and past messages to generate responses based solely on the given information.

        *Text to base your answers on:*
        {text_block}

        *Past messages and answers for context:*
        {text_past_messages}

        *User's question or statement:*
        {text}

        *Instructions:*
        - Answer concisely and precisely as if you were the text's author.
        - Use the provided text as the primary source.
        - Utilize past messages for additional context but do not repeat them.
        - If the user's input is a statement respond with Understood or Entendido if it is in spanish, if you can't answer the question with the provided texts simply answer that you cannot answer with the available information.
        - If the user's input is "Why?" or "Explain more" or "go deeper" or any question like that take into account the last question and explain it more into detail.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert assistant chatbot having a conversation with a user. You examine texts and return responses based solely on the information contained within the texts and past messages for context. You answer questions precisely and briefly only utilizing the provided text and past messages for context.",
                },
                {
                    "role": "user",
                    "content": whole_prompt,
                },
            ],
            max_tokens=300,
            temperature=0
        )
        #Pendiente y posiblemente deprecado
        #self._vector_store.store_messages(document_id, text, response.choices[0].message.content)
        
        doc_ref = self.db.collection("Documents").document(document_id).collection("PastMessages").document(response_id)
        doc_ref.set({"id": message_id, "content": response.choices[0].message.content, "userID": user_id, "role": "chat", "documentID": document_id, "timestamp": now})
        #Se regresa el Id de la pregunta aunque no sea el ID de este mensaje en especifico para facilitar highlighteo en frontend.
        return MessageContent(message=response.choices[0].message.content, mes_id= message_id, role="chat")

    def extract_message(self, document_id: str, text: str, user_id: str) -> MessageContent:
        message = self._message_completion(document_id=document_id, text=text, vector_store=self._vector_store,user_id=user_id)
        return message