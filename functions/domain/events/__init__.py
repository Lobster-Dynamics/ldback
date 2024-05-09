from enum import Enum 

from .document_created import DocumentCreatedEvent # type: ignore

class FiridaEventType(Enum):
    DOCUMENT_CREATED = "DOCUMENT_CREATED"

