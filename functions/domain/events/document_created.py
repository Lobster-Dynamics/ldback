from pydantic import BaseModel, ConfigDict, Field 

class DocumentCreatedEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    creator_id: str = Field() 
    document_id: str = Field()