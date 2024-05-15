import json
from typing import List

from openai import OpenAI
from domain.document.ivector_store import IVectorStore, ResultingChunk
from domain.document.ichat_answers import IChatAnswers
from functions.domain.document.ichat_answers import MessageContent
from infrastructure.vector_store.vector_store import VectorStore

class OpenAIChatExtractor(IChatAnswers):
    def __init__(self, api_key: str, vector_store: IVectorStore):
        # TODO: parametryze configuration params
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self._vector_store = vector_store
    
    def _message_completion(self, document_id: str, text: str, vector_store: IVectorStore) -> str:
        chunks = vector_store.get_similar_chunks(document_id, 3, text)
        text_block = ""
        for i in range(len(chunks)):
            text_block += chunks[i].text
        
        whole_prompt = f"""
        This is the text you should base your answers from: {text_block}, you should answer concisely, meaning briefly and precisely, as if you were the text's author. \n
        Here is the question to answer: {text}\n
        """
        response = self.client.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert assistant chatbot meant to examinate texts and return reponses based soleley on the information contained within the texts. You answer to the questions precisely and briefly.",
                },
                {
                    "role": "user",
                    "content": whole_prompt,
                },
            ],
            max_tokens=300,
            temperature=0
        )
        return response.choices[0].message.content

    def extract_message(self, document_id: str, text: str) -> MessageContent:
        return MessageContent(
            message=self._message_completion(document_id=document_id, text=text, vector_store=self._vector_store)
        )