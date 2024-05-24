from abc import ABC, abstractmethod

from .user import User


class IUserRepo(ABC):
    @abstractmethod
    def add(self, item: User): ...

    @abstractmethod
    def get(self, id: str) -> User: ...

    @abstractmethod
    def update(self, item: User): ...

    @abstractmethod
    def get_with_email(self, email: str) -> User: ...
