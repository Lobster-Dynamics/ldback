from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel, ConfigDict, Field

from .document import BiblioGraphicInfo, Summary, KeyConcept, Relationship
from .ivector_store import IVectorStore

class TextInsight(BaseModel):
    model_config = ConfigDict(frozen=True)

    bibliografic_info: BiblioGraphicInfo | None = Field()
    key_concepts: List[KeyConcept] = Field()
    summary: Summary = Field()
    relationships: List[Relationship] = Field()


class ITextInsightExtractor(ABC):

    @abstractmethod
    def extract_insight(self, document_id: str, text_chunks: List[str], text_vector_store: IVectorStore) -> TextInsight: ...
