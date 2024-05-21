from pydantic import BaseModel, AnyUrl
from typing import Dict, List

class Volunteer(BaseModel):
    organization: str = ""
    position: str = ""
    url: AnyUrl = None
    website: AnyUrl = None
    start_date: str = ""
    end_date: str = ""
    summary: str = ""
    highlights: List[str] = []
    location: str = ""
    start: Dict[str, int] = {}
    end: Dict[str, int] = {}
    