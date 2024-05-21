import hashlib
import httpx
from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Query, status, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm


from app.utils.security import authenticate_user, create_access_token

from app.models.user import OauthToken
from loguru import logger


router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

@router.post("/login", response_model=OauthToken)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> OauthToken:
    """Login to get an access token."""
    db_user = await authenticate_user(form_data.username, form_data.password)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Generate a JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": form_data.username},
        expires_delta=access_token_expires
    )

    return OauthToken(
        access_token=access_token,
        token_type="bearer"
    )
    


    