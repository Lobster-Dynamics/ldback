from typing import TypeVar, Generic
from abc import ABC, abstractmethod

EventType = TypeVar("EventType")


class ISubscriber(ABC, Generic[EventType]):
    @abstractmethod
    async def notify(self, event: EventType): ...

