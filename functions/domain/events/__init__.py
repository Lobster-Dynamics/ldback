from enum import Enum 

from .document_created import DocumentCreatedEvent # type: ignore
from .document_shared import DocumentSharedEvent # type: ignore

class FiridaEventType(Enum):
    DOCUMENT_CREATED = "DOCUMENT_CREATED"

