from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models.experience import Experience, ExperienceInCreate, ExperienceInDB, ExperienceInResponse, ExperienceInUpdate
from app.models.user import User
from app.database.db import experience_collection, user_collection
from app.utils.security import get_current_user
from bson import ObjectId


router = APIRouter()


@router.post("/", response_model=ExperienceInResponse, status_code=status.HTTP_201_CREATED, summary="Create new experience")
async def create_experience(experience_data: ExperienceInCreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create a new experience"""
    if not experience_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input."
        )
    experience = await experience_collection.find_one({
        "$and": [
            {"name": experience_data.name},
            {"company": experience_data.company}
        ]
    })

    if experience:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Experience already exists."
        )
    
    try:
        db_experience = ExperienceInDB(**experience_data.model_dump())
        db_experience.created_at = datetime.now(timezone.utc)
        db_experience.updated_at = datetime.now(timezone.utc)
        db_experience.owner = current_user.username

        new_experience = await experience_collection.insert_one(db_experience.model_dump())

        if new_experience:
            return ExperienceInResponse(
                message="Experience created successfully.",
                id=new_experience.inserted_id
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create experience."
        )
    
@router.get("/", response_model=list[Experience], status_code=status.HTTP_200_OK, summary="Get all experiences")
async def get_expereinces(current_user: Annotated[User, Depends(get_current_user)]):
    """Get all experiences"""
    experience_owner = await user_collection.find_one({"username": current_user.username})
    if current_user and not experience_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to retrieve experiences."
        )
    
    experience_exist = await experience_collection.find_one({"owner": current_user.username})
    if not experience_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No experiences found."
        )
    
    experiences = []
    try:
        async for experience in experience_collection.find({"owner": current_user.username}):
            experiences.append(Experience(**experience))
        return experiences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve experiences."
        )
    
@router.get("/{id}", response_model=Experience, status_code=status.HTTP_200_OK, summary="Get an experience")
async def get_experience(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get an Experience"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    experience_exist = await experience_collection.find_one({"_id": ObjectId(id)})

    if not experience_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experience not found."
            )
    if experience_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    try:
        return Experience(**experience_exist)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve experience."
        )
    
@router.patch("/{id}", response_model=ExperienceInResponse, status_code=status.HTTP_200_OK, summary="Update experience")
async def update_experience(id: str, exp_update_data: ExperienceInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update a single experience."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    experience_exist = await experience_collection.find_one({"_id": ObjectId(id)})

    if not experience_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found."
        )
    if experience_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    try:
        experience_data = ExperienceInUpdate(**exp_update_data.model_dump(exclude_unset=True))
        experience_data.updated_at = datetime.now(timezone.utc)

        update_data = experience_data.model_dump(exclude={"created_at"}, exclude_unset=True)
        await experience_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        updated_experience = await experience_collection.find_one({"_id": ObjectId(id)})
        if updated_experience:
            return ExperienceInResponse(
                message="Experience updated successfully.",
                id=updated_experience["_id"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update experience."
        )
    

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete experience")
async def delete_dexperience(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Delete experience"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    experience_exist = await experience_collection.find_one({"_id": ObjectId(id)})

    if not experience_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found."
        )
    if experience_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    try:
        await experience_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete experience."
        )
    
