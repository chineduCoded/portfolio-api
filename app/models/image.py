from pydantic import BaseModel

class ImageResolution(BaseModel):
    url: str = ""
    size: int = 0
    width: int = 0
    height: int = 0

class ImageResolutions(BaseModel):
    micro: ImageResolution
    thumbnail: ImageResolution
    mobile: ImageResolution
    desktop: ImageResolution

class Image(BaseModel):
    resolutions: ImageResolutions
