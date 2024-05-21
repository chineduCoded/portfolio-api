from datetime import datetime, timezone
from typing import Annotated
from fastapi import status, APIRouter, Depends, HTTPException
from app.models.certification import Certification, CertificationInCreate, CertificationInResponse, CertificationInDB, CertificationInUpdate
from app.models.user import User
from app.utils.security import get_current_user
from app.database.db import certification_collection
from bson import ObjectId


router = APIRouter()


@router.post("/", response_model=CertificationInResponse, status_code=status.HTTP_201_CREATED)
async def create_certificate(certificate_data: CertificationInCreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create certification"""
    if not certificate_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input."
        )
    
    existing_certification = await certification_collection.find_one({"name": certificate_data.name})

    if existing_certification:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Certificate already exist."
        )
    
    try:
        certificate = CertificationInDB(**certificate_data.model_dump())
        certificate.owner = current_user.username
        certificate.created_at = datetime.now(timezone.utc)
        certificate.updated_at = datetime.now(timezone.utc)

        certificate_saved = await certification_collection.insert_one(certificate.model_dump())
        return CertificationInResponse(
            message="Certificate created successfully.",
            id=certificate_saved.inserted_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create certificate.{e}"
        )
    

@router.get("/", response_model=list[Certification], status_code=status.HTTP_200_OK)
async def get_certifications(current_user: Annotated[User, Depends(get_current_user)]):
    """Get all certifications"""
    certification_owner = await certification_collection.find_one({"owner": current_user.username})
    if not certification_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to retrieve certifications."
        )
    
    certifications = []

    try:
        async for certification in certification_collection.find({"owner": current_user.username}):
            certifications.append(Certification(**certification))
        return certifications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve certifications."
        )
    
@router.get("/{id}", response_model=Certification, status_code=status.HTTP_200_OK)
async def get_certification(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get certification"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    certificate_exist = await certification_collection.find_one({"_id": ObjectId(id)})

    if not certificate_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cerficate not found."
        )
    
    if certificate_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not authorized."
        )
    
    try:
        return Certification(**certificate_exist)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cerfiticate."
        )
    
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certification(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Delete certificate"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    certificate_exist = await certification_collection.find_one({"_id": ObjectId(id)})

    if not certificate_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cerficate not found."
        )
    
    if certificate_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not authorized."
        )
    
    try:
        await certification_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete cerfiticate."
        )
    

@router.patch("/{id}", response_model=CertificationInResponse, status_code=status.HTTP_200_OK)
async def update_certification(id: str, update_data: CertificationInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update certification"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    certificate_exist = await certification_collection.find_one({"_id": ObjectId(id)})

    if not certificate_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cerficate not found."
        )
    
    if certificate_exist["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not authorized."
        )
    
    try:
        certificate_data = CertificationInUpdate(**update_data.model_dump(exclude_unset=True))
        certificate_data.updated_at = datetime.now(timezone.utc)

        certificate_update = certificate_data.model_dump(exclude={"created_at"}, exclude_unset=True)
        await certification_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": certificate_update}
        )

        updated_certificate = await certification_collection.find_one({"_id": ObjectId(id)})
        if updated_certificate:
            return CertificationInResponse(
                message="Certificate updated successfully.",
                id=updated_certificate["_id"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update certificate."
        )