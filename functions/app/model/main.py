import json
from typing import List
from uuid import uuid1, UUID
from enum import Enum
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class User(BaseModel):

    model_config = ConfigDict(validate_assignment=True)

    id: str = Field()
    name: str = Field(min_length=4, max_length=15)
    lastname: str = Field(min_length=4, max_length=15)
    email: EmailStr = Field()
    root_directory_id: UUID = Field(alias="rootDirectoryId")

    @classmethod
    def create_new(cls): ...


class ContainedItemType(Enum):
    DIRECTORY = "DIRECTORY"
    DOCUMENT = "DOCUMENT"


class ContainedItem(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    item_type: ContainedItemType = Field(alias="itemType")
    item_id: UUID = Field(alias="itemId")


class Directory(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field()
    name: str = Field()
    owner_id: UUID = Field(alias="ownerId")
    contained_items: List[ContainedItem] = Field(alias="containedItems")


class UserPrivilegeLevelOnDocument(Enum):
    READ_ONLY = "READ_ONLY"
    READ_AND_WRITE = "READ_AND_WRITE"


class UserWithAccessData(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    user_id: UUID = Field(alias="userId")
    privilege_level: UserPrivilegeLevelOnDocument = Field(alias="privilegeLevel")


class AuthorData(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    name: str = Field()
    surnames: List[str] = Field()


class BiblioGraphicInfo(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    authors: List[AuthorData] = Field()
    title: str = Field()
    publisher: str = Field()
    publishment_date: date = Field(alias="publishmentDate")


class SummarySection(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    title: str = Field()
    body: str = Field()


class Summary(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    secctions: List[SummarySection] = Field()


class KeyConcept(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field()
    name: str = Field()
    description: str = Field()
    relationships: List[UUID] = Field()


class Relationship(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    father_concept_id: UUID = Field(alias="fatherConceptId")
    child_concept_id: UUID = Field(alias="childConceptId")
    description: str = Field()


class Document(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field()
    owner_id: UUID = Field(alias="ownerId")
    id_raw_doc: UUID = Field(alias="idRawDoc")
    parsed_llm_input: str = Field(alias="parsedLLMInput")
    users_with_access: List[UserWithAccessData] = Field(alias="usersWithAccess")
    bibliographic_info: BiblioGraphicInfo = Field(alias="biblioGraficInfo")
    summary: Summary = Field()
    key_concepts: List[KeyConcept] = Field(alias="keyConcepts")
    relationships: List[Relationship] = Field()


##### ENDPOINT REQUESTS ######


class CreateDocumentRequest(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    owner_id: UUID = Field(alias="ownerId")
    document_name: str = Field(alias="documentName")


schemas = [User, Directory, Document, CreateDocumentRequest]

SCHEMAS_BASE_DIR = "./json_schemas/"


def create_json_schemas():
    for schema in schemas:
        json_schema = schema.model_json_schema()
        with open(f"{SCHEMAS_BASE_DIR}{json_schema['title']}.schema.json", "w") as f:
            f.write(json.dumps(json_schema, indent=2))


def main():
    create_json_schemas()


if __name__ == "__main__":
    main()
