from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.basic_info import BasicInfoCreate, BasicInfoResponse, BasicInfoInDB, BasicInfoInDBOut, BasicInfoInUpdate
from app.models.user import User
from app.utils.security import get_current_user
from app.database.db import basicinfo_collection
from bson import ObjectId


router = APIRouter()


@router.post("/", response_model=BasicInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_basic_info(basic_info_data: BasicInfoCreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create the basic information of the portfolio"""

    if not basic_info_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input."
        )
    
    existing_basic_info = await basicinfo_collection.find_one({
        "$or": [
            {"phone_number": basic_info_data.phone_number},
           { "website_url": basic_info_data.website_url}
        ]
    })

    if existing_basic_info:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The basic info already exists."
        )
    
    try:
        basic_data = BasicInfoInDB(**basic_info_data.model_dump())
        basic_data.created_at = datetime.now(timezone.utc)
        basic_data.updated_at = datetime.now(timezone.utc)
        basic_data.owner = current_user.username

        new_data = await basicinfo_collection.insert_one(basic_data.model_dump())

        return BasicInfoResponse(
            message="Basic info created successfully.",
            id=new_data.inserted_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create basic info."
        )


@router.get("/{id}", response_model=BasicInfoInDBOut, status_code=status.HTTP_200_OK)
async def get_basic_info(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get the basic information of the portfolio"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )

    basic_info_data = await basicinfo_collection.find_one({"_id": ObjectId(id)})

    if not basic_info_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found."
        )
    
    if basic_info_data["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    

    
    return BasicInfoInDBOut(**basic_info_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_basic_info(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Delete the basic info data
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    basic_info_data = await basicinfo_collection.find_one({"_id": ObjectId(id)})

    if not basic_info_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found."
        )
    
    if basic_info_data["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    await basicinfo_collection.delete_one({"_id": ObjectId(id)})


@router.patch("/{id}", response_model=BasicInfoResponse, status_code=status.HTTP_200_OK)
async def update_basic_info(
    id: str, 
    update_data: BasicInfoInUpdate, 
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update basic info data"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )

    basic_info_data = await basicinfo_collection.find_one({"_id": ObjectId(id)})

    if not basic_info_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Basic info not found."
        )
    
    if basic_info_data["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    try:
        basic_info_update = BasicInfoInUpdate(**update_data.model_dump(exclude_unset=True))
        basic_info_update.updated_at = datetime.now(timezone.utc)

        basic_data = basic_info_update.model_dump(exclude={"created_at"}, exclude_unset=True)

        await basicinfo_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": basic_data}
        )

        updated_basic_info = await basicinfo_collection.find_one({"_id": ObjectId(id)})

        return BasicInfoResponse(
            message="Basic info updated successfully.",
            id=updated_basic_info["_id"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failde to update basic info."
        )