from typing import Any
from typing import Tuple, Optional, List, TypeVar, Generic
from io import BytesIO
from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field


class DocumentImage(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str = Field()

    data: Any = Field()


ContentType = TypeVar("ContentType")


class DocSection(BaseModel, Generic[ContentType]):
    model_config = ConfigDict(frozen=True)

    index: int = Field()
    content: ContentType = Field()


class ParsingResult(BaseModel):
    """Defines the structure of the parsing result returned by Parser classes
    implementing the IParser interface.
    The parsing result must contain a list of contents
    The parsing result  must have
    an array of text_sections and an array of image_sections. These image sections must
    specify the content of the section and the index, the index of a section wether it is a text
    section or image section, describes its position in the page as a whole. This is
    so that we can concatenate images with texts so that the render of this structure
    reasembles the original structure of the document that was parsed.
    """

    model_config = ConfigDict(frozen=True)

    text_sections: List[DocSection[str]] = Field()
    image_sections: List[DocSection[Any]] = Field()


class IParser(ABC):
    """Takes a file determined by the implementation of the interface and
    returns an object of type Parsing Result
    """

    @abstractmethod
    def parse(self, file: BytesIO) -> ParsingResult: ...
