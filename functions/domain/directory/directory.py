from typing import List
from uuid import UUID
from enum import Enum
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ContainedItemType(str, Enum):
    DIRECTORY = "DIRECTORY"
    DOCUMENT = "DOCUMENT"


class ContainedItem(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    item_type: ContainedItemType = Field(alias="itemType")
    item_id: UUID = Field(alias="itemId")

class DocumentToDelete(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    doc_id: str = Field()
    directory_id: str = Field()


class Directory(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field()
    name: str = Field()
    owner_id: str = Field(alias="ownerId")
    contained_items: List[ContainedItem] = Field(None, alias="containedItems")
    shared_users: Optional[List[str]] = Field(None, alias="sharedUsers")
    parent_id: Any = Field(None, alias="parentId")
    upload_date: datetime = Field(alias="uploadDate")
