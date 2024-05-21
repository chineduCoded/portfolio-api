from datetime import datetime, timezone
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.interest import Interest, InterestInCreate, InterestInDB, InterestInResponse, InterestInUpdate
from app.models.user import User
from app.database.db import interest_collection, user_collection
from app.utils.security import get_current_user
from bson import ObjectId


router = APIRouter()


@router.post("/", response_model=InterestInResponse, status_code=status.HTTP_201_CREATED)
async def create_interest(interest_data: InterestInCreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create a new interest"""
    if not interest_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid interest data")
    
    existing_interest = await interest_collection.find_one({"name": interest_data.name})
    if existing_interest:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Interest already exists."
        )
    
    try:
        interest = InterestInDB(**interest_data.model_dump())
        interest.owner = current_user.username
        interest.created_at = datetime.now(timezone.utc)
        interest.updated_at = datetime.now(timezone.utc)

        interest_saved = await interest_collection.insert_one(interest.model_dump())

        return InterestInResponse(message="Interest created successfully", id=interest_saved.inserted_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interest."
        )
    
@router.get("/", response_model=List[Interest], status_code=status.HTTP_200_OK)
async def get_interests(current_user: Annotated[User, Depends(get_current_user)]):
    """Get all interests"""
    interest_owner = await user_collection.find_one({"username": current_user.username})
    if not interest_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to retrieve interests."
        )
    
    interests = []
    
    try:
        async for interest in interest_collection.find({"owner": current_user.username}):
            interests.append(Interest(**interest))
        return interests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interests."
        )
    

@router.get("/{id}", response_model=Interest, status_code=status.HTTP_200_OK)
async def get_interest(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get a single interest"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    interest = await interest_collection.find_one({"_id": ObjectId(id)})

    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interest not found."
        )
    
    if interest["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to access this interest."
        )
    
    try:
        return Interest(**interest)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interest."
        )
    
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interest(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Delete an interest"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    interest = await interest_collection.find_one({"_id": ObjectId(id)})

    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interest not found."
        )
    
    if interest["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete this interest."
        )
    
    try:
        await interest_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete interest."
        )
    
@router.patch("/{id}", response_model=InterestInResponse, status_code=status.HTTP_200_OK)
async def update_interest(id: str, interest_data: InterestInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update an interest"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    interest = await interest_collection.find_one({"_id": ObjectId(id)})

    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interest not found."
        )
    
    if interest["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update this interest."
        )
    
    try:
        interest_update = InterestInUpdate(**interest_data.model_dump(exclude_unset=True))
        interest_update.updated_at = datetime.now(timezone.utc)

        interest_excluded = interest_update.model_dump(exclude={"created_at"}, exclude_unset=True)
        await interest_collection.update_one({"_id": ObjectId(id)}, {"$set": interest_excluded})

        updated_interest = await interest_collection.find_one({"_id": ObjectId(id)})
        if updated_interest:
            return InterestInResponse(
                message="Interest updated successfully",
                id=updated_interest["_id"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update interest."
        )