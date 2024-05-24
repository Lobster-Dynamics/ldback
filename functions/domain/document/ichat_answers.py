from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from .ivector_store import IVectorStore, ResultingChunk


class MessageContent(BaseModel):
    model_config = ConfigDict(frozen=True)

    # id: str = Field()
    message: str = Field()
    # role: str = Field()


class IChatAnswers(ABC):
    """Interface meant to utilize the embeddings stored on the vector database to answer questions, the available tokens are split
    between chunks, previous message context, the question and the answer.
    """
    
    @abstractmethod 
    def extract_message(self, document_id: str, user_id: str, text: str) -> MessageContent: 
        """Assembles the message into the required format for storage and posterior usage.
        """
