from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional
from .custom_types import PydanticObjectId

class CertificationBase(BaseModel):
    name: str
    certified_url: str
    organization: str = ""
    date_achieved: datetime = None
    description: str = ""
    owner: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



class CertificationInCreate(BaseModel):
    name: str
    certified_url: str
    organization: str = ""
    date_achieved: datetime = None

    @validator("date_achieved", pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v


class CertificationInDB(CertificationBase):
    pass

class CertificationInResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class CertificationInUpdate(BaseModel):
    name: Optional[str] = None
    certified_url: Optional[str] = None
    organization: Optional[str] = None
    date_achieved: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Certification(CertificationBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )