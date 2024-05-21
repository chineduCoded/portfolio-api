from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import List, Optional
from .custom_types import PydanticObjectId

class EducationBase(BaseModel):
    institution: str
    url: str = ""
    course_studied: str
    study_type: str
    comment: str = ""
    courses: List[str] = []
    description: str = ""
    activities: str = ""
    gpa: Optional[float] = 0.0
    owner: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EducationInCreate(BaseModel):
    institution: str
    course_studied: str
    study_type: str
    description: str = ""

    

class EducationInDB(EducationBase):
    pass

class EducationInResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class EducationInUpdate(BaseModel):
    institution: Optional[str] = None
    url: Optional[str] = None
    course_studied: Optional[str] = None
    study_type: Optional[str] = None
    comment: Optional[str] = None
    courses: Optional[List[str]] = None
    description: Optional[str] = None
    activities: Optional[str] = None
    gpa: Optional[float] = None
    updated_at: Optional[datetime] = None


class Education(EducationBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )