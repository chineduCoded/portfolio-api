from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.education import Education, EducationInCreate, EducationInDB, EducationInResponse, EducationInUpdate
from app.models.user import User
from app.utils.security import get_current_user
from app.database.db import education_collection, user_collection
from bson import ObjectId


router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EducationInResponse)
async def create_education(education_data: EducationInCreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create new education"""
    if not education_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input."
        )
    existing_education = await education_collection.find_one({"study_type": education_data.study_type})

    if existing_education:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Education already exists."
        )
    
    try:
        db_education = EducationInDB(**education_data.model_dump())
        db_education.created_at = datetime.now(timezone.utc)
        db_education.updated_at = datetime.now(timezone.utc)
        db_education.owner = current_user.username

        new_education = await education_collection.insert_one(db_education.model_dump())

        return EducationInResponse(
            message="Education created successfully",
            id=new_education.inserted_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create education."
        )

@router.get("/", response_model=List[Education], status_code=status.HTTP_200_OK, summary="Get all the educations")
async def get_educations(current_user: Annotated[User, Depends(get_current_user)]):
    """Get all educations"""
    education_owner = await user_collection.find_one({"username": current_user.username})
    if current_user and not education_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to retrieve references."
        )
    
    educations = []
    try:
        async for education in education_collection.find({"owner": current_user.username}):
            educations.append(Education(**education))
        return educations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve educations. {e}"
        )
    
@router.get("/{id}", response_model=Education, status_code=status.HTTP_200_OK, summary="Get a specific education")
async def get_education(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get a specific education"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    education = await education_collection.find_one({"_id": ObjectId(id)})
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found."
        )
    
    if education["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed to retrieve education."
        )
    
    try:
        return Education(**education)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve educations."
        )
    
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a specific education")
async def delete_education(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Delete a specific education"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    education = await education_collection.find_one({"_id": ObjectId(id)})
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found."
        )
    
    if education["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed to retrieve education."
        )
    
    try:
        await education_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve education."
        )
    
@router.patch("/{id}", response_model=EducationInResponse, status_code=status.HTTP_200_OK, summary="Update a specific education")
async def update_education(id: str, education_data: EducationInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update a specific education"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    education = await education_collection.find_one({"_id": ObjectId(id)})
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found."
        )
    
    if education["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed to retrieve education."
        )
    
    try:
        education_update = EducationInUpdate(**education_data.model_dump(exclude_unset=True))
        education_update.updated_at = datetime.now(timezone.utc)
        exclude_field_update = education_update.model_dump(exclude={"created_at"}, exclude_unset=True)

        await education_collection.update_one({"_id": ObjectId(id)}, {"$set": exclude_field_update})
        
        updated_education = await education_collection.find_one({"_id": ObjectId(id)})

        if updated_education:
            return EducationInResponse(
                message="Education updated successfully",
                id=updated_education["_id"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update education. {e}"
        )