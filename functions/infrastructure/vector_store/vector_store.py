import json
from typing import List
from pinecone import Pinecone
from openai import OpenAI
from domain.document.ivector_store import IVectorStore, ResultingChunk
import uuid

class VectorStore(IVectorStore): 
    def __init__(self, op_api_key: str, pc_api_key: str):
        # TODO: parametryze configuration params
        self.op = OpenAI(api_key=op_api_key)
        self.model = "text-embedding-3-small"
        self.pc = Pinecone(api_key=pc_api_key)
        self.index=self.pc.Index("embedding-storage")
    
    def insert(self, document_id: str, text: str) -> str: 
        chunk_id = str(uuid.uuid1())

        response = self.op.embeddings.create(
            input=text,
            model=self.model
        )
        self.index.upsert(
            vectors=[
                {"id":chunk_id, "values":response.data[0].embedding, "metadata":{"ChunkText":text}}
            ],
            namespace=document_id
        )
        return chunk_id


    def get_similar_chunks(self, document_id: str, k: int, text: str) -> List[ResultingChunk]: 
        response = self.op.embeddings.create(
            input=text,
            model=self.model
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