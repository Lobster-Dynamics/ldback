import json
from typing import List
from pinecone import Pinecone
from openai import OpenAI
from domain.document.ivector_store import IVectorStore, ResultingChunk, ResultingMessage
import uuid

class VectorStore(IVectorStore): 
    def __init__(self, op_api_key: str, pc_api_key: str):
        # TODO: parametryze configuration params
        self.op = OpenAI(api_key=op_api_key)
        self.model = "gpt-3.5-turbo"
        self.pc_model = "text-embedding-3-small"
        self.pc = Pinecone(api_key=pc_api_key)
        self.index=self.pc.Index("embedding-storage")
        self.index_messages=self.pc.Index("past-messages")
    
    def store_messages(self, document_id: str, message: str, answer:str) -> str:
        interaction_id = str(uuid.uuid1())
        
        question_answer = f"""
        {message} : {answer}
        """
        response = self.op.embeddings.create(
            input=question_answer,
            model=self.pc_model
        )
        self.index_messages.upsert(
            vectors=[
                {"id":interaction_id, "values":response.data[0].embedding, "metadata":{"Question":message, "Answer":answer}}
            ],
            namespace=document_id
        )
        return interaction_id

    def insert(self, document_id: str, text: str) -> str: 
        chunk_id = str(uuid.uuid1())

        response = self.op.embeddings.create(
            input=text,
            model=self.pc_model
        )
        self.index.upsert(
            vectors=[
                {"id":chunk_id, "values":response.data[0].embedding, "metadata":{"ChunkText":text}}
            ],
            namespace=document_id
        )
        return chunk_id
    
    def deleteNamespace(self, document_id: str) -> str:
        self.index.delete(delete_all=True, namespace=document_id)
        self.index_messages.delete(delete_all=True, namespace=document_id)
        return document_id

    def get_similar_past_messages(self, document_id: str, k: int, text: str) -> List[ResultingMessage]: 
        ...
        response = self.op.embeddings.create(
            input=text,
            model=self.pc_model
        )
        result=self.index_messages.query(
            namespace=document_id,
            vector=response.data[0].embedding,
            top_k=k,
            include_values=False,
            include_metadata=True
        )
        messages = []
        for i in range(len(result.matches)):
            messages.append(ResultingMessage(
                id=result.matches[i].id,
                question=result.matches[i].metadata["Question"],
                answer=result.matches[i].metadata["Answer"],
                similarity=result.matches[i].score
            ))
        return messages

    def get_similar_chunks(self, document_id: str, k: int, text: str) -> List[ResultingChunk]: 
        response = self.op.embeddings.create(
            input=text,
            model=self.pc_model
        )
        result=self.index.query(
            namespace=document_id,
            vector=response.data[0].embedding,
            top_k=k,
            include_values=False,
            include_metadata=True
        )
        chunks = []
        for i in range(len(result.matches)):
            chunks.append(ResultingChunk(
                id=result.matches[i].id,
                text=result.matches[i].metadata["ChunkText"],
                similarity=result.matches[i].score
            ))
        return chunks