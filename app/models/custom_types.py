from typing import Annotated, Any
from  pydantic import PlainSerializer, AfterValidator, WithJsonSchema, BaseModel
from bson import ObjectId


# Custom Pydantic ObjectId type
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PydanticObjectId = Annotated[
    str | ObjectId,
    PlainSerializer(lambda x: str(x), return_type=str, when_used="json"),
    AfterValidator(validate_object_id),
    WithJsonSchema({
        "type": "string"
    }, mode="serialization")
]
