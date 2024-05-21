from abc import ABC, abstractmethod
from typing import Optional
from .keyconcept import KeyConcept


class IKeyConceptRepo(ABC):
    @abstractmethod
    def add(self, item: KeyConcept) -> None:
        """
        Add a KeyConcept item to the repository.
        """
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        """
        Delete a KeyConcept item from the repository by its ID.
        """
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[KeyConcept]:
        """
        Retrieve a KeyConcept item from the repository by its ID.
        """
        pass

