from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Union, Annotated
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config import settings
from app.models.user import User, UserInDB, OauthTokenData
from app.utils.hashing import verify_password
from app.database.db import user_collection




oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.token_url)

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = "HS256"

async def get_user(db, username: str) -> UserInDB | None:
    """Retrieves a user from the database by username."""
    db_user = await db.find_one({"username": username})

    if db_user:
        return UserInDB(**db_user)
    else:
        return None
    
async def authenticate_user(username: str, password: str) -> UserInDB | None:
    """
    Authenticates a user by checking username and password.

    Args:
        username (str): The username of the user to authenticate.
        password (str): The password provided by the user.

    Returns:
        User: The authenticated user object if successful, None otherwise.
    """
    user = await get_user(user_collection, username)

    if not user:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid credentials."
            )
            
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials."
        )
    
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)

    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_refresh_secret_key, algorithm=ALGORITHM)

    return encoded_jwt



async def verify_access_token(token: str, credentials_exception):
    """Verify access token"""
     
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("username")

        if username is None:
            raise credentials_exception
        
        return OauthTokenData(username=username)
    
    except JWTError:
        raise credentials_exception

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Fetches the current user based on an OAuth2 token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Await the result of verify_access_token
    token_data = await verify_access_token(token, credentials_exception)

    return token_data


