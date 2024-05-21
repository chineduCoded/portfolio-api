from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from .custom_types import PydanticObjectId

class ExperienceBase(BaseModel):
    name: str
    company: str
    description: str
    summary: List[str]
    position: str = ""
    url: str = ""
    start_date: datetime | str
    end_date: datetime | str
    highlights: List[str] = []
    is_current_role: bool = False
    website: str = ""
    owner: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ExperienceInCreate(BaseModel):
    name: str
    company: str
    description: str
    summary: List[str]
    position: str = ""
    is_current_role: bool = False
    start_date: datetime | str
    end_date: datetime | str

class ExperienceInDB(ExperienceBase):
    pass

class ExperienceInResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class ExperienceInUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[List[str]] = None
    position: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[datetime | str] = None
    end_date: Optional[datetime | str] = None
    highlights: Optional[List[str]] = None
    is_current_role: Optional[bool] = None
    website: Optional[str] = None
    updated_at: Optional[datetime] = None

class Experience(ExperienceBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )