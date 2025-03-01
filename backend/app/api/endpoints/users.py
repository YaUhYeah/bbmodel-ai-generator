from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.models.user import User, UserCreate, UserUpdate
from app.services.auth import get_current_user, get_password_hash
from app.db.crud import create_user, get_user_by_email, get_users

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_new_user(user_in: UserCreate):
    """
    Create a new user
    """
    user = get_user_by_email(user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.dict(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    
    return create_user(user_data)

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user
    """
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user
    """
    if user_in.password:
        hashed_password = get_password_hash(user_in.password)
        current_user.hashed_password = hashed_password
    
    user_data = user_in.dict(exclude={"password"}, exclude_unset=True)
    
    for field, value in user_data.items():
        setattr(current_user, field, value)
    
    # In a real implementation, this would update the user in the database
    # For now, we'll just return the updated user
    return current_user