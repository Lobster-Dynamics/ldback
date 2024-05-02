from uuid import uuid1, UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):

    model_config = ConfigDict(validate_assignment=True)

    id: str = Field(frozen=True)
    name: str = Field(min_length=4, max_length=15)
    lastname: str = Field(min_length=4, max_length=15)
    email: EmailStr = Field()
    password: str = Field()
    root_directory_id: UUID = Field(alias="rootDirectoryId")

    @classmethod
    def create_new(
        cls, name: str, lastname:str, email: EmailStr, password: str, root_directory_id: UUID
    ) -> "User":
        return cls(
            id=uuid1(),
            name=name,
            lastname=lastname,
            email=email,
            password=password,
            rootDirectoryId=root_directory_id,
        )
