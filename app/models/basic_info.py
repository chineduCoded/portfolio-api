from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import List, Optional, Union, Annotated
from pydantic_extra_types.country import CountryAlpha2, CountryAlpha3
from .custom_types import PydanticObjectId


class Profile(BaseModel):
    platform: str = ""
    username: str = ""
    url: str = ""


class BasicInfo(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    label: str = ""
    phone_number: List[Annotated[str, Field(..., description="Phone number", pattern="^(?:\+?234)?(080|081|090|070|091)[0-9]{8}$")]]
    website_url: str = ""
    summary: str = ""
    location: str = ""
    profiles: List[Profile] = []
    headline: str = ""
    years_of_experience: int = 0
    region: str = ""
    country: str = ""
    country_code: Union[CountryAlpha2, CountryAlpha3] = "NG"
    owner: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BasicInfoCreate(BasicInfo):
    pass

class BasicInfoInDB(BasicInfo):
    pass


class BasicInfoResponse(BaseModel):
    message: str
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class BasicInfoInDBOut(BasicInfo):
    id: PydanticObjectId = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        populate_by_alias=True,
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

class BasicInfoInUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    label: Optional[str] = ""
    phone_number: Optional[List[Annotated[str, Field(..., description="Phone number", pattern="^(?:\+?234)?(080|081|090|070|091)[0-9]{8}$")]]] = None
    website_url: Optional[str] = ""
    summary: Optional[str] = ""
    location: Optional[str] = ""
    profiles: Optional[List[Profile]] = None
    headline: Optional[str] = ""
    years_of_experience: Optional[int] = 0
    region: Optional[str] = ""
    country: Optional[str] = ""
    country_code: Optional[Union[CountryAlpha2, CountryAlpha3]] = "NG"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None