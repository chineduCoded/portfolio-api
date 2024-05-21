from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .custom_types import PydanticObjectId


class InterestBase(BaseModel):
    name: str
    description: str = ""
    owner: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InterestInCreate(BaseModel):
    name: str
    description: str = ""


class InterestInDB(InterestBase):
    pass

class InterestInResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class InterestInUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Interest(InterestBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )