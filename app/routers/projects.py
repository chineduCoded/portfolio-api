from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from pydantic import ValidationError
from app.models.project import ProjectCreate, ProjectInDB, Project, ProjectInResponse, ProjectInUpdate
from app.models.user import User
from app.database.db import project_collection, user_collection
from app.utils.security import get_current_user
from bson import ObjectId


router = APIRouter()

@router.post("/", response_model=ProjectInResponse, status_code=status.HTTP_201_CREATED, summary="Create new project")
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user)):
    """Create a new project"""
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input."
        )
    
    project = await project_collection.find_one({"name": project_data.name})

    if project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project already exists."
        )
    
    try:
        db_project = ProjectInDB(**project_data.model_dump())
        db_project.created_at = datetime.now(timezone.utc)
        db_project.updated_at = datetime.now(timezone.utc)
        db_project.owner = current_user.username

        new_project = await project_collection.insert_one(db_project.model_dump())

        if new_project:
            return ProjectInResponse(
                message="Project created successfully.",
                id=new_project.inserted_id
            )
    except ValidationError as exc:
        errors = [f"Field: {error['loc'][0]}, Error: {error['msg']}" for error in exc.errors()]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="\n".join(errors)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project. {e}"
        )
    
@router.get("/", response_model=list[Project], status_code=status.HTTP_200_OK, summary="Get all projects")
async def get_projects(limits: int = 10, current_user: User = Depends(get_current_user)):
    """Get all projects"""
    project_owner = await user_collection.find_one({"username": current_user.username})

    if current_user and not project_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to retrieve projects."
        )
    
    project_exist = await project_collection.find_one({"owner": current_user.username})
    if not project_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't have any projects."
        )
    
    projects = []
    try:
        async for project in project_collection.find({"owner": current_user.username}).limit(limits):
            projects.append(Project(**project))
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve projects. {e}"
        )
    
@router.get("/{id}", response_model=Project, status_code=status.HTTP_200_OK, summary="Get project by ID")
async def get_project(id: str, current_user: User = Depends(get_current_user)):
    """Get project by ID"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    project = await project_collection.find_one({"_id": ObjectId(id)})

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    
    if project["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to retrieve this project."
        )
    
    try:
        return Project(**project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project. {e}"
        )

@router.patch("/{id}", response_model=ProjectInResponse, status_code=status.HTTP_200_OK, summary="Update a project")
async def update_project(id: str, project_data: ProjectInUpdate, current_user: User = Depends(get_current_user)):
    """Update a project"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    project = await project_collection.find_one({"_id": ObjectId(id)})

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    
    if project["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this project."
        )
    
    try:
        project_update = ProjectInUpdate(**project_data.model_dump(exclude_unset=True))
        project_update.updated_at = datetime.now(timezone.utc)

        project_update_dumped = project_update.model_dump(exclude={"created_at"}, exclude_unset=True)

        await project_collection.update_one({"_id": ObjectId(id)}, {"$set": project_update_dumped})

        updated_project = await project_collection.find_one({"_id": ObjectId(id)})

        if updated_project:
            return ProjectInResponse(
                message="Project updated successfully.",
                id=updated_project["_id"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project. {e}"
        )
    

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete project")
async def delete_project(id: str, current_user: User = Depends(get_current_user)):
    """Delete a project"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    project = await project_collection.find_one({"_id": ObjectId(id)})

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    
    if project["owner"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this project."
        )
    
    try:
        await project_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project."
        )