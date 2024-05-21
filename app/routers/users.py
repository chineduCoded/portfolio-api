from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import APIRouter, status, HTTPException, Depends
from app.models.user import UserInCreate, UserInResponse, UserInDB, User, CountUser, UserInUpdate
from app.database.db import user_collection
from app.utils.hashing import get_hashed_password
from pymongo import ASCENDING
from bson import ObjectId
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=UserInResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserInCreate):
    """Register a new user."""
    await user_collection.create_index([("username", ASCENDING), ("email", ASCENDING)])

    existing_user = await user_collection.find_one({
        "$or": [
            {"username": user.username},
            {"email": user.email}
        ]
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User account already exists."
        )

    db_user = UserInDB(**user.model_dump())
    db_user.password = get_hashed_password(user.password)
    db_user.created_at = datetime.now(timezone.utc)

    
    try:
        new_user = await user_collection.insert_one(db_user.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user."
        )
    
    return UserInResponse(
        message="User created successfully",
        id=new_user.inserted_id
    )

@router.get("/count", response_model=CountUser, status_code=status.HTTP_200_OK)
async def count_users():
    """Count the total number of users"""
    total_users = await user_collection.count_documents({})

    return CountUser(total_users=total_users)


@router.get("/", response_model=List[User], status_code=status.HTTP_200_OK)
async def get_users(length: int = 10):
    """Get all users"""
    users = await user_collection.find().to_list(length=length)

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found in the database."
        )
    
    return [User(**user) for user in users]


@router.get("/me", response_model=User, status_code=status.HTTP_200_OK)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get me"""
    user = await user_collection.find_one({"username": current_user.username})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
    
    if user["username"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized."
        )
    
    try:
        return User(**user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user."
        )



@router.get("/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(id: str, current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get a user"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    user = await user_collection.find_one({"_id": ObjectId(id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist."
        )

    if user["username"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized."
        )
    
    try:
        return User(**user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user."
        )




@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Delete a user"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    user = await user_collection.find_one({"_id": ObjectId(id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist."
        )
        
    if user["username"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized."
        )

    try:
        await user_collection.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user."
        )


@router.patch("/{id}", response_model=UserInResponse, status_code=status.HTTP_200_OK)
async def update_user(id: str, user_data: UserInUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    """Update a user"""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object ID."
        )
    
    user = await user_collection.find_one({"_id": ObjectId(id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist."
        )

    if user["username"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update other user's information."
        )
    
    try:
        user_update = UserInUpdate(**user_data.model_dump(exclude_unset=True))
        user_update.updated_at = datetime.now(timezone.utc)

        if user_update.password:
            user_update.password = get_hashed_password(user_update.password)
        
        update_data = user_update.model_dump(exclude={"created_at"}, exclude_unset=True)
        # update_data = {k:v for k, v in user_update.model_dump().items() if v is not None}

        await user_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )

        updated_user = await user_collection.find_one({"_id": ObjectId(id)})

        if updated_user:
            return UserInResponse(
                message="User updated successfully",
                id=updated_user["_id"]
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user."
        )
