from datetime import datetime
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from .custom_types import PydanticObjectId


class ReferenceBase(BaseModel):
    name: str
    position: str = ""
    company: str = ""
    email: EmailStr
    phone_number: Optional[Annotated[str, Field("", description="Phone number", pattern="^(?:\+?234)?(080|081|090|070|091)[0-9]{8}$")]]
    relationship: str = ""
    years_known: int = 0
    is_verified: bool = False
    owner: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReferenceIncreate(BaseModel):
    name: str
    position: str = ""
    company: str = ""
    email: EmailStr
    phone_number: Optional[Annotated[str, Field("", description="Phone number", pattern="^(?:\+?234)?(080|081|090|070|091)[0-9]{8}$")]]

class ReferenceInDB(ReferenceBase):
    pass

class ReferenceResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class ReferenceInUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[Annotated[str, Field("", description="Phone number", pattern="^(?:\+?234)?(080|081|090|070|091)[0-9]{8}$")]] = None
    relationship: Optional[str] = None
    years_known: Optional[int] = None
    is_verified: Optional[bool] = None
    updated_at: Optional[datetime] = None

class Reference(ReferenceBase):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )