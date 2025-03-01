from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VisibilityType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    UNLISTED = "unlisted"

class LikeBase(BaseModel):
    user_id: str
    model_id: str

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class CommentBase(BaseModel):
    user_id: str
    model_id: str
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

class FollowBase(BaseModel):
    follower_id: str
    followed_id: str

class FollowCreate(FollowBase):
    pass

class Follow(FollowBase):
    id: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class NotificationType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    SYSTEM = "system"

class NotificationBase(BaseModel):
    user_id: str
    type: NotificationType
    content: str
    related_id: Optional[str] = None  # ID of the related model, comment, etc.
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class ModelShareBase(BaseModel):
    model_id: str
    visibility: VisibilityType = VisibilityType.PRIVATE
    allow_comments: bool = True
    allow_downloads: bool = False
    tags: List[str] = []

class ModelShareCreate(ModelShareBase):
    pass

class ModelShare(ModelShareBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    download_count: int = 0
    
    model_config = {
        "from_attributes": True
    }