from pydantic import BaseModel, ConfigDict 

class DocumentSharedEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

