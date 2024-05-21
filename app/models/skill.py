from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from pydantic import Field, ConfigDict
from .custom_types import PydanticObjectId

class SkillBase(BaseModel):
    name: str
    level: str
    keywords: List[str] = []
    rating: float
    years_of_experience: int
    owner: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SkillInCreate(BaseModel):
    name: str
    level: str
    keywords: List[str] = []
    rating: float
    years_of_experience: int 


class SkillInDB(SkillBase):
    pass


class SkillResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class Skill(SkillBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class SkillInUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    keywords: Optional[List[str]] = []
    rating: Optional[float] = None
    years_of_experience: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None