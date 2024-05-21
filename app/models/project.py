from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, validator
import validators
from typing import List, Optional, Annotated
from . image import Image
from . video import Video
from .custom_types import PydanticObjectId

class ProjectBase(BaseModel):
    name: str
    description: str = ""
    summary: str = ""
    image_url: str =  ""
    video_url: str =  ""
    github_repository_url: str =  ""
    project_live_url: str =   ""
    primary_language: str = ""
    languages: List[str] = []
    libraries: List[str] = []
    frameworks: List[str] = []
    tools: List[str] = []
    tags: List[str] = []
    owner: str = ""
    start_date: Optional[datetime] = None 
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    summary: str = ""
    image_url: str =  ""
    video_url: str =  ""
    github_repository_url: str =  ""
    project_live_url: str =   ""
    primary_language: str = ""
    languages: List[str] = []
    libraries: List[str] = []
    frameworks: List[str] = []
    tools: List[str] = []
    tags: List[str] = []
    start_date: Optional[datetime] = None 
    end_date: Optional[datetime] = None

    @validator("start_date", "end_date", pre=True)
    def parse_dates(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
    
    @validator("github_repository_url", "project_live_url", "image_url","video_url", pre=True)
    def validate_urls(cls, v):
        if v == "":
            return v
        
        if not validators.url(v):
            raise ValueError(f"{v} is not a valid URL")
        return v
    
class ProjectInDB(ProjectBase):
    pass

class ProjectInResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class ProjectInUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    images: Optional[str] = None
    videos: Optional[str] = None
    github_repository_url: Optional[str] = None
    project_live_url: Optional[str] = None
    primary_language: Optional[str] = None
    languages: Optional[List[str]] = None
    libraries: Optional[List[str]] = None
    frameworks: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    start_date: Optional[datetime] = None 
    end_date: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator("start_date", "end_date", pre=True)
    def parse_dates(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v

    @validator("github_repository_url", "project_live_url", pre=True)
    def validate_urls(cls, v):
        if not validators.url(v):
            raise ValueError(f"{v} is not a valid URL")
        return v


class Project(ProjectBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )