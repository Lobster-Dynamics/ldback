import json
from typing import List

from openai import OpenAI
from domain.document.ivector_store import IVectorStore, ResultingChunk
from domain.document.iopenai_fragment import IFragmentExplanation
from domain.document.ichat_answers import MessageContent
from domain.document.iopenai_fragment import FragmentContent
from domain.document.document import ExplanationFragment
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

    def _fragment_explanation(self, document_id: str, query: str, vector_store: IVectorStore) -> ExplanationFragment:
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
        
        explanation_text = response.choices[0].message.content

        title_prompt = f"""
INSTRUCCIONES:
Proporciona un título breve y conciso para la siguiente explicación.
No contestes nada mas que con el titulo que generes no le agregues un preambulo o una explicacion antes, solo el titulo.


EXPLICACIÓN:
{explanation_text}
        """

        title_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Tu eres un asistente experto que proporciona títulos breves para explicaciones.",
                },
                {
                    "role": "user",
                    "content": title_prompt,
                },
            ],
            max_tokens=100,
            temperature=0
        )
        
        explanation_title = title_response.choices[0].message.content.strip()

        return ExplanationFragment(titulo=explanation_title, texto=explanation_text)

    def extract_fragment(self, document_id: str, query: str) -> FragmentContent:
        explanation_fragment = self._fragment_explanation(document_id=document_id, query=query, vector_store=self._vector_store)
        
        # Fetch the document from Firestore
        doc_ref = self.db.collection('Documents').document(document_id)
        doc = doc_ref.get()
        
        # Check if the document exists and if the 'historicexplanations' field exists
        if doc.exists:
            doc_data = doc.to_dict()
            if 'historicexplanations' in doc_data:
                historic_explanations = doc_data['historicexplanations']
            else:
                historic_explanations = []
        else:
            # If the document doesn't exist, initialize the historic explanations list
            historic_explanations = []
        
        # Append the new explanation fragment
        historic_explanations.append({"texto": explanation_fragment.texto, "titulo": explanation_fragment.titulo })
        
        # Update the document with the new list
        doc_ref.set({'historicexplanations': historic_explanations}, merge=True)
        
        return FragmentContent(explanation=explanation_fragment.texto)
