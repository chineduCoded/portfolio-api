from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.reference import Reference, ReferenceInDB, ReferenceInUpdate, ReferenceIncreate, ReferenceResponse
from app.models.user import User
from app.database.db import reference_collection, user_collection
from app.utils.security import get_current_user
from bson import ObjectId


router = APIRouter()


@router.post("/", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_reference(reference: ReferenceIncreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create a new reference"""
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input."
        )

    existing_reference = await reference_collection.find_one({"name": reference.name})
    if existing_reference:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reference already exists."
        )

    try:
        db_reference = ReferenceInDB(**reference.model_dump())
        db_reference.created_at = datetime.now(timezone.utc)
        db_reference.updated_at = datetime.now(timezone.utc)
        db_reference.owner = current_user.username

        new_reference = await reference_collection.insert_one(db_reference.model_dump())

        return ReferenceResponse(
            message="Reference created successfully",
            id=new_reference.inserted_id
        )
    except Exception as e:
        # logger.error(f"Error creating reference: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reference."
        )
    
@router.get("/", response_model=List[Reference], status_code=status.HTTP_200_OK)
async def get_references(current_user: Annotated[User, Depends(get_current_user)]):
    """Get all references"""
    reference_owner = await user_collection.find_one({"username": current_user.username})
    if current_user and not reference_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to retrieve references."
        )
    
    references = []
    
    try:
        async for reference in reference_collection.find({"owner": current_user.username}):
            references.append(Reference(**reference))
        return references
    except Exception as e:
        # logger.error(f"Error retrieving references: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve references."
        )
    
@router.get("/{id}", response_model=Reference, status_code=status.HTTP_200_OK)
async def get_reference(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get a reference"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    reference_exist = await reference_collection.find_one({"_id": ObjectId(id)})
    if not reference_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found."
        )
    
    if reference_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to retrieve reference."
        )
    try:
        return Reference(**reference_exist)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reference."
        )
    
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reference(id: str, current_user:Annotated[User, Depends(get_current_user)]):
    """Delete a reference"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    reference_exist = await reference_collection.find_one({"_id": ObjectId(id)})
    if not reference_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found."
        )
    
    if reference_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete reference."
        )
    try:
        await reference_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete reference."
        )
    
@router.patch("/{id}", response_model=ReferenceResponse, status_code=status.HTTP_200_OK)
async def update_reference(id: str, update_data: ReferenceInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update reference"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    reference_exist = await reference_collection.find_one({"_id": ObjectId(id)})
    if not reference_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found."
        )
    
    if reference_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update reference."
        )
    try:
        reference_update = ReferenceInUpdate(**update_data.model_dump(exclude_unset=True))
        reference_update.updated_at = datetime.now(timezone.utc)

        reference_excluded = reference_update.model_dump(exclude={"created_at"}, exclude_unset=True)
        await reference_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": reference_excluded}
        )

        updated_reference = await reference_collection.find_one({"_id": ObjectId(id)})
        if updated_reference:
            return ReferenceResponse(
                message="Reference updated successfully",
                id=updated_reference["_id"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reference."
        )