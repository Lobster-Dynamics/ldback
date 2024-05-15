from typing import List
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, ConfigDict 

class ResultingChunk(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: str = Field()
    text: str = Field()
    similarity: float = Field()

class IVectorStore(ABC):
    """Interface meant to represent a vector store build
    of chunks of a specific document. 
    """
    
    @abstractmethod 
    def insert(self, document_id: str, text: str) -> str: 
        """Embeds the text 'text' and inserts it 
        in a vector database. Returns the ID of the vector 
        for further retrieval
        """

    @abstractmethod
    def get_similar_chunks(self, document_id: str, k: int, text: str) -> List[ResultingChunk]: 
        """ Embeds the text and returns the 
        k most similar chunks to the embedded text
        """
    
    abstractmethod
    def deleteNamespace(self, document_id: str) -> str: 
        """ Deletes the whole namespace given to it as document_id
        """
