from typing import List, Optional
from uuid import uuid1

from pydantic import BaseModel, ConfigDict, Field


class KeyConcept(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str = Field(default_factory=lambda: str(uuid1()))
    name: str = Field(..., description="Name of the key concept")
    description: Optional[str] = None
    relationships: Optional[List[str]] = None
