from typing import Any
from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field


class Email(BaseModel):
    model_config = ConfigDict(frozen=True)
    subject: str = Field()
    body: str = Field()
    to_email: str = Field()


class IEMAIL(ABC):
    @abstractmethod
    def send_email(self, subject: str, body: str, to_email: str) -> None:
        pass
