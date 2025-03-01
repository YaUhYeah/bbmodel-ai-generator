from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    CREATOR = "creator"
    MODERATOR = "moderator"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    social_links: Optional[dict] = None

class UserProfile(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    social_links: Optional[dict] = None
    follower_count: int = 0
    following_count: int = 0
    model_count: int = 0
    
    model_config = {
        "from_attributes": True
    }

class User(UserBase):
    id: str
    created_at: datetime
    profile: Optional[UserProfile] = None
    token_balance: int = 0
    
    model_config = {
        "from_attributes": True
    }

class UserPublic(BaseModel):
    id: str
    username: str
    full_name: Optional[str] = None
    role: UserRole
    profile: Optional[UserProfile] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }