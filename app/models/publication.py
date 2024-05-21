from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Dict, Optional
from .custom_types import PydanticObjectId

class PublicationBase(BaseModel):
    title: str
    author: str
    release_date: datetime
    summary: str = ""
    full_release_date: datetime = None
    publication_url: str = ""
    owner: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PublicationInCreate(BaseModel):
    title: str
    author: str
    release_date: datetime
    summary: str = ""
    full_release_date: datetime = None
    publication_url: str = ""

    @validator("release_date", "full_release_date", pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v


class PublicationInDB(PublicationBase):
    pass

class PublicationResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class PublicationInUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    release_date: Optional[datetime] = None
    summary: Optional[str] = None
    full_release_date: Optional[datetime] = None
    publication_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Publication(PublicationBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )