from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from .ivector_store import IVectorStore, ResultingChunk


class FragmentContent(BaseModel):
    model_config = ConfigDict(frozen=True)

    # id: str = Field()
    explanation: str = Field()


class IFragmentExplanation(ABC):
    """Interface meant to utilize the embeddings stored on the vector database to explain fragments, the available tokens are split
    between chunks, the question and the answer.
    """
    
    @abstractmethod 
    def extract_fragment(self, document_id: str, query: str) -> FragmentContent: 
        """Assembles the explanation into the required format.
        """
