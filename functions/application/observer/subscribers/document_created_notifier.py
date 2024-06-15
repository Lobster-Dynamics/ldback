from abc import ABC, abstractmethod
from typing import Dict, Any

from domain.events import DocumentCreatedEvent, FiridaEventType

from ..isubscriber import ISubscriber

# this notifier
class INotifier(ABC):
    @abstractmethod
    async def notify_user(self, user_id: str, msg: Dict[Any, Any]):
        """Sends a notification to user and if not able to send a notification then it
        raises and error
        """


class DocumentUploadedNotifier(ISubscriber[DocumentCreatedEvent]):
    """ Is in charged of notifying the user when a document that he has commanded
    to be uploaded has been created"""

    def __init__(self, notifier: INotifier):
        self._notifier = notifier

    async def notify(self, event: DocumentCreatedEvent):
        await self._notifier.notify_user(
            event.creator_id,
            msg={
                "event_type": FiridaEventType.DOCUMENT_CREATED.value,
                "data": {"document_id": event.document_id},
            },
        )
