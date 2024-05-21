from datetime import datetime, timezone, date
from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Depends
from app.models.publication import Publication, PublicationInCreate, PublicationInUpdate, PublicationResponse, PublicationInDB
from app.models.user import User
from app.database.db import publication_collection, user_collection
from app.utils.security import get_current_user
from bson import ObjectId


router = APIRouter()


@router.post("/", response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_publication(publication_data: PublicationInCreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create a new publication"""

    if not publication_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data")
    
    existing_publication = await publication_collection.find_one({"title": publication_data.title})

    if existing_publication:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Publication already exists")
    
    try:
        publication = PublicationInDB(**publication_data.model_dump())

        publication.created_at = datetime.now(timezone.utc)
        publication.updated_at = datetime.now(timezone.utc)
        publication.owner = current_user.username

        response = await publication_collection.insert_one(publication.model_dump())

        if response:
            return PublicationResponse(message="Publication created successfully.", id=response.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create publication. {e}")
    

@router.get("/", response_model=list[Publication], status_code=status.HTTP_200_OK)
async def get_publications(current_user: Annotated[User, Depends(get_current_user)]):
    """Get all publications"""
    publication_owner = await user_collection.find_one({"username": current_user.username})
    if current_user and not publication_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to retrieve publications."
        )
    
    publications = []
    try:
        async for publication in publication_collection.find({"owner": current_user.username}):
            publications.append(Publication(**publication))
        return publications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve publications."
        )
    

@router.get("/{id}", response_model=Publication, status_code=status.HTTP_200_OK)
async def get_publication(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get a publication"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    publication_exist = await publication_collection.find_one({"_id": ObjectId(id)})

    if not publication_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publiction not found."
            )
    if publication_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    try:
        return Publication(**publication_exist)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve publication."
        )
    
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Delete publication"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    publication_exist = await publication_collection.find_one({"_id": ObjectId(id)})

    if not publication_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found."
        )
    if publication_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    try:
        await publication_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete publication."
        )
    

@router.patch("/{id}", response_model=PublicationResponse, status_code=status.HTTP_200_OK)
async def update_publication(id: str, pub_update_data: PublicationInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update a publication"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )

    if not pub_update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input."
        )
    
    publication_exist = await publication_collection.find_one({"_id": ObjectId(id)})

    if not publication_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found."
        )
    if publication_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    try:
        publication_data = PublicationInUpdate(**pub_update_data.model_dump(exclude_unset=True))
        publication_data.updated_at = datetime.now(timezone.utc)

        update_data = publication_data.model_dump(exclude={"created_at"}, exclude_unset=True)
        await publication_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        updated_publication = await publication_collection.find_one({"_id": ObjectId(id)})
        if updated_publication:
            return PublicationResponse(
                message="Publication updated successfully.",
                id=updated_publication["_id"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update publication."
        )