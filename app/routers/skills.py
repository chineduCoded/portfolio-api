from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from app.database.db import skill_collection
from app.models.skill import SkillInCreate, SkillResponse, SkillInDB, Skill, SkillInUpdate
from app.models.user import User
from app.utils.security import get_current_user
from bson import ObjectId

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SkillResponse)
async def create_skill(skill_data: SkillInCreate, current_user: Annotated[User, Depends(get_current_user)]):
    """Create a new skill"""
    
    if not skill_data:
         raise HTTPException(
              status_code=status.HTTP_400_BAD_REQUEST,
              detail="Invalid input."
         )

    
    existing_skill = await skill_collection.find_one({"name": skill_data.name})

    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A skill with that name already exists."
        )

    try: 
         db_skill = SkillInDB(**skill_data.model_dump())
         db_skill.created_at = datetime.now(timezone.utc)
         db_skill.updated_at = datetime.now(timezone.utc)
         db_skill.owner = current_user.username

         new_skill = await skill_collection.insert_one(db_skill.model_dump())

         return SkillResponse(
              message="Skill created successfully",
              id=new_skill.inserted_id
         )
    except Exception as e:
        #  logger.error(f"Error creating skill: {str(e)}")
         raise HTTPException(
              status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Failed to create skill."
         )
    
@router.get("/", response_model=list[Skill], status_code=status.HTTP_200_OK)
async def get_skills(current_user: Annotated[User, Depends(get_current_user)]):
    """Get all the skills"""
    skill_owner = await skill_collection({"owner": current_user.username})
    if not skill_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to retrieve skills."
        )
    
    skills = []
    
    try:
        async for skill in skill_collection.find({"owner": current_user.username}):
            skills.append(Skill(**skill))
        return skills
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve skill."
        )

@router.get("/{id}", response_model=Skill, status_code=status.HTTP_200_OK)
async def get_skill(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Get a skill"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    skill = await skill_collection.find_one({"_id": ObjectId(id)})

    if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found."
            )
    if skill["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    try:
        return Skill(**skill)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve skill."
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Delete a skill"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    skill = await skill_collection.find_one({"_id": ObjectId(id)})

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found."
        )
    
    if skill["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    try:
        await skill_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete skill."
        )


@router.patch("/{id}", response_model=SkillResponse, status_code=status.HTTP_200_OK)
async def update_skill(id: str, skill_update_data: SkillInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update a skill"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    skill = await skill_collection.find_one({"_id": ObjectId(id)})

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found."
        )
    
    if skill["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    try:
        skill_data = SkillInUpdate(**skill_update_data.model_dump(exclude_unset=True))
        skill_data.updated_at = datetime.now(timezone.utc)

        skill_update = skill_data.model_dump(exclude={"created_at"}, exclude_unset=True)

        await skill_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": skill_update}
        )

        updated_skill = await skill_collection.find_one({"_id": ObjectId(id)})

        return SkillResponse(
            message="Skill updated successfully.",
            id=updated_skill["_id"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update skill."
        )