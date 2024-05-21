from datetime import datetime
from pydantic import BaseModel, validator, Field, ConfigDict
from .custom_types import PydanticObjectId
from typing import Optional

class AwardBase(BaseModel):
    title: str
    date: datetime
    awarder: str
    summary: str = ""
    full_date: datetime = None
    owner: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AwardInCreate(BaseModel):
    title: str
    date: datetime
    awarder: str
    summary: str = ""
    full_date: datetime = None

    @validator("date", "full_date", pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
    
class AwardInResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class AwardInDB(AwardBase):
    pass

class AwardInUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    awarder: Optional[str] = None
    summary: Optional[str] = None
    full_date: datetime = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Award(AwardBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )