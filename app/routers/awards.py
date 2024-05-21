from datetime import datetime, timezone
from typing import Annotated
from fastapi import status, APIRouter, Depends, HTTPException
from app.models.award import AwardInDB, AwardInCreate, AwardInResponse, AwardInUpdate, Award
from app.models.user import User
from app.database.db import award_collection
from app.utils.security import get_current_user
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=AwardInResponse, status_code=status.HTTP_201_CREATED)
async def create_award(award_data: AwardInCreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create award"""
    if not award_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input."
        )
    
    existing_award = await award_collection.find_one({"title": award_data.title})

    if existing_award:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Award already exist."
        )
    
    try:
        award = AwardInDB(**award_data.model_dump())
        award.owner = current_user.username
        award.created_at = datetime.now(timezone.utc)
        award.updated_at = datetime.now(timezone.utc)

        award_saved = await award_collection.insert_one(award.model_dump())

        return AwardInResponse(
            message="Award created successfully.",
            id=award_saved.inserted_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create award."
        )
    

@router.get("/", response_model=list[Award], status_code=status.HTTP_200_OK)
async def get_awards(current_user: Annotated[User, Depends(get_current_user)]):
    """Get all awards"""
    award_owner = await award_collection.find_one({"owner": current_user.username})
    if not award_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to retrieve awards."
        )
    
    awards = []
    
    try:
        async for award in award_collection.find({"owner": current_user.username}):
            awards.append(Award(**award))
        return awards
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve awards."
        )
    
@router.get("/{id}", response_model=Award, status_code=status.HTTP_200_OK)
async def get_award(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get award."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    award_exist = await award_collection.find_one({"_id": ObjectId(id)})

    if not award_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Award not found."
        )
    
    if award_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    try:
        return Award(**award_exist)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve award."
        )
    
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_award(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Delete award"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    award_exist = await award_collection.find_one({"_id": ObjectId(id)})

    if not award_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Award not found."
        )
    
    if award_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    try:
        await award_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete award."
        )
    
@router.patch("/{id}", response_model=AwardInResponse, status_code=status.HTTP_200_OK)
async def update_award(id: str, update_data: AwardInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update award"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    award_exist = await award_collection.find_one({"_id": ObjectId(id)})

    if not award_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Award not found."
        )
    
    if award_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    try:
        updated_data = AwardInUpdate(**update_data.model_dump(exclude_unset=True))
        updated_data.updated_at = datetime.now(timezone.utc)

        update_award = updated_data.model_dump(exclude={"created_at"}, exclude_unset=True)

        await award_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_award}
        )

        updated_award = await award_collection.find_one({"_id": ObjectId(id)})
        if updated_award:
            return AwardInResponse(
                message="Award updated successfully.",
                id=updated_award["_id"]
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update award."
        )