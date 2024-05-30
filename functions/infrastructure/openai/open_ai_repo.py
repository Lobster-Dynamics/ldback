import json
from typing import List

from openai import OpenAI
from domain.document.ivector_store import IVectorStore, ResultingChunk
from domain.document.iopenai_fragment import IFragmentExplanation
from domain.document.ichat_answers import MessageContent
from domain.document.iopenai_fragment import FragmentContent
from infrastructure.vector_store.vector_store import VectorStore
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter


import uuid
import datetime


class OpenAIFragmentExtractor(IFragmentExplanation):
    def __init__(self, api_key: str, vector_store: IVectorStore):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self._vector_store = vector_store
        self.db = firestore.client()
    
    def _fragment_explanation(self, document_id: str, query: str, vector_store: IVectorStore) -> str:
        chunks = vector_store.get_similar_chunks(document_id, 3, query)
        text_block = "\n".join([chunk.text for chunk in chunks])



        whole_prompt = f"""
INSTRUCCIONES:
Proporciona una respuesta concisa que explique detalladamente el contenido del fragmento del documento (FRAGMENTO A EXPLICAR) proporcionado.
Utiliza como referencia las partes del mismo documento que se te entregarán (PARTES DE CONOCIMIENTO). Si estas no son suficientes, puedes usar tus propios conocimientos para completar la explicación.
La respuesta DEBE ser una explicación del fragmento dado; no debes agregar información no solicitada.
Si el FRAGMENTO A EXPLICAR y las PARTES DE CONOCIMIENTO están en otro idioma, debes dar la explicación en ese mismo idioma.

PARTES DE CONOCIMIENTO
{text_block}
Fin de PARTES DE CONOCIMIENTO

FRAGMENTO A EXPLICAR
{query}
Fin de FRAGMENTO A EXPLICAR
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Tu eres un asistente experto que recibe pedazos de un documento de investigacion los cuales tienes que utilizar para explicar un fragmento des ese mismo documento.",
                },
                {
                    "role": "user",
                    "content": whole_prompt,
                },
            ],
            max_tokens=1000,
            temperature=0
        )
        
        return response.choices[0].message.content

    def extract_fragment(self, document_id: str, query: str) -> FragmentContent:
        explanation = self._fragment_explanation(document_id=document_id, query=query, vector_store=self._vector_store)
        return FragmentContent(explanation=explanation)
    
    