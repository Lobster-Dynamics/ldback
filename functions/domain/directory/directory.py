from typing import List
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ContainedItemType(str, Enum):
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
    owner_id: str = Field(alias="ownerId")
    contained_items: List[ContainedItem] = Field(None, alias="containedItems")
