from abc import ABC, absractmethod

from pydantic import BaseModel, ConfigDict, Field


class Email(BaseModel):
    model_config = ConfigDict(frozen=True)
    subject: str = Field()
    body: str = Field()
    to_email: str = Field()


class DocumentImage(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str = Field()

    data: Any = Field()


class IEMAIL(ABC):
    @absractmethod
    def send_email(self, subject: str, body: str, to_email: str) -> None:
        pass
