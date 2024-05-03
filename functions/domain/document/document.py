from datetime import date
from typing import List, Optional
from enum import Enum


from pydantic import BaseModel, ConfigDict, Field


class UserPrivilegeLevelOnDocument(Enum):
    READ_ONLY = "READ_ONLY"
    READ_AND_WRITE = "READ_AND_WRITE"


class UserWithAccessData(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    user_id: str = Field(alias="userId")
    privilege_level: UserPrivilegeLevelOnDocument = Field(alias="privilegeLevel")

class WordCloud(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    text: str = Field()
    value: int = Field()


class AuthorData(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    name: str = Field()
    surnames: List[str] = Field()


class BiblioGraphicInfo(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    authors: List[AuthorData] = Field()
    title: str = Field()
    publisher: str = Field()
    publishment_date: Optional[date] = Field(alias="publishmentDate")


class SummarySection(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    title: str = Field()
    body: str = Field()


class Summary(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    secctions: List[SummarySection] = Field()


class KeyConcept(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str = Field()
    name: str = Field()
    description: str = Field()
    relationships: List[str] = Field()


class Relationship(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    father_concept_id: str = Field(alias="fatherConceptId")
    child_concept_id: str = Field(alias="childConceptId")
    description: str = Field()

class DocumentImage(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    location: str = Field()
    url: str = Field()

class ParsedLLMInput(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    content: List[str] = Field()
    image_sections: Optional[List[DocumentImage]] = Field(alias="imageSections")


class Document(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: str = Field()
    owner_id: str = Field(alias="ownerId")
    id_raw_doc: str = Field(alias="idRawDoc")
    name: str = Field(alias="name")
    extension: str = Field(alias="extension")
    parsed_llm_input: ParsedLLMInput = Field(alias="parsedLLMInput")
    users_with_access: List[UserWithAccessData] = Field(alias="usersWithAccess")
    bibliographic_info: Optional[BiblioGraphicInfo] = Field(
        None, alias="biblioGraficInfo"
    )
    summary: Optional[Summary] = None
    key_concepts: Optional[List[KeyConcept]] = Field(None, alias="keyConcepts")
    relationships: Optional[List[Relationship]] = None
