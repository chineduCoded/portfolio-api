from pydantic import BaseModel

class Video(BaseModel):
    url: str = ""
    source: str = ""
    source_id: str = ""