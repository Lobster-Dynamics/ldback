import json
from typing import List

from openai import OpenAI
from domain.document.ivector_store import IVectorStore, ResultingChunk
from domain.document.ichat_answers import IChatAnswers
from domain.document.ichat_answers import MessageContent
from infrastructure.vector_store.vector_store import VectorStore

class OpenAIChatExtractor(IChatAnswers):
    def __init__(self, api_key: str, vector_store: IVectorStore):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self._vector_store = vector_store
    
    def _message_completion(self, document_id: str, text: str, vector_store: IVectorStore) -> str:
        chunks = vector_store.get_similar_chunks(document_id, 3, text)
        text_block = "\n".join([chunk.text for chunk in chunks])
        
        messages = vector_store.get_similar_past_messages(document_id, 3, text)
        text_messages = "\n".join([f"{msg.question}: {msg.answer}" for msg in messages])

        whole_prompt = f"""
        You are an expert assistant chatbot having a conversation with a user. Your role is to examine the provided texts and past messages to generate responses based solely on the given information.

        *Text to base your answers on:*
        {text_block}

        *Past messages and answers for context:*
        {text_messages}

        *User's question or statement:*
        {text}

        *Instructions:*
        - Answer concisely and precisely as if you were the text's author.
        - Use the provided text as the primary source.
        - Utilize past messages for additional context but do not repeat them.
        - If the user's input is a statement respond with Understood, if you can't answer the question with the provided texts simply answer that you cannot answer with the available information.
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
        self._vector_store.store_messages(document_id, text, response.choices[0].message.content)
        return response.choices[0].message.content

    def extract_message(self, document_id: str, text: str) -> MessageContent:
        message = self._message_completion(document_id=document_id, text=text, vector_store=self._vector_store)
        print(message)
        return MessageContent(
            message=message
        )