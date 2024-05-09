from typing import DefaultDict, List, Any, Dict
from collections import defaultdict
import json

from domain.events import DocumentCreatedEvent, FiridaEventType

from .isubscriber import ISubscriber

class Observer(object):
    def __init__(self):
        self._subscribers: DefaultDict[type, List[ISubscriber[type]]] = defaultdict(
            list
        )

    def add_listener(self, subscriber: ISubscriber[Any], event: type):
        self._subscribers[event].append(subscriber)

    async def notify_raw_event(self, event_raw: bytes):
        event_data: Dict[Any, Any] = json.loads(event_raw)
        # swtich for all event types
        if event_data["event_type"] == FiridaEventType.DOCUMENT_CREATED.value:
            event = DocumentCreatedEvent.model_validate(event_data["data"])
            await self.notify_event(event)

    async def notify_event(self, event: Any):
        for sub in self._subscribers[type(event)]:
            await sub.notify(event)

 