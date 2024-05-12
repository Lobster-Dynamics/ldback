from abc import ABC, abstractmethod

from .document import Document


class IDocumentRepo(ABC):
    @abstractmethod
    def add(self, item: Document): ...

    @abstractmethod
    def get(self, id: str) -> Document: ...

    @abstractmethod
    def update(self, item: Document): ...

    @abstractmethod
    def delete(self, id: str): ...
