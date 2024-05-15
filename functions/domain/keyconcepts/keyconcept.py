from uuid import uuid1
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class KeyConcept(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str = Field(default_factory=lambda: str(uuid1()))
    name: str = Field(..., description="Name of the key concept")
    description: str = Field(..., description="Description of the key concept")
    relationships: List[str] = Field(default_factory=list, description="List of related concepts")
