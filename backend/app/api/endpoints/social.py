from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.base import get_db
from app.db import crud
from app.models.social import Like, Comment, Follow, Notification
from app.models.bbmodel import BBModelPublic
from app.services.auth import get_current_user
from app.models.user import User, UserPublic

router = APIRouter()

@router.get("/public-models", response_model=List[BBModelPublic])
async def get_public_models(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get public models with optional search
    """
    models = crud.get_public_models(db, skip, limit, search)
    
    # Convert to BBModelPublic with username
    result = []
    for model in models:
        user = crud.get_user(db, model.user_id)
        model_dict = model.__dict__.copy()
        model_dict["username"] = user.username if user else "Unknown"
        result.append(model_dict)
    
    return result

@router.post("/models/{model_id}/like")
async def like_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like a model
    """
    model = crud.get_model(db, model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    like = crud.like_model(db, current_user.id, model_id)
    return {"message": "Model liked successfully"}

@router.delete("/models/{model_id}/like")
async def unlike_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlike a model
    """
    success = crud.unlike_model(db, current_user.id, model_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )
    
    return {"message": "Model unliked successfully"}

@router.post("/models/{model_id}/comment", response_model=Comment)
async def add_comment(
    model_id: str,
    content: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a comment to a model
    """
    model = crud.get_model(db, model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    comment = crud.add_comment(db, {
        "user_id": current_user.id,
        "model_id": model_id,
        "content": content
    })
    
    return comment

@router.get("/models/{model_id}/comments", response_model=List[Comment])
async def get_model_comments(
    model_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get comments for a model
    """
    model = crud.get_model(db, model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return crud.get_model_comments(db, model_id, skip, limit)

@router.post("/users/{user_id}/follow")
async def follow_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Follow a user
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    follow = crud.follow_user(db, current_user.id, user_id)
    return {"message": f"You are now following {user.username}"}

@router.delete("/users/{user_id}/follow")
async def unfollow_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unfollow a user
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = crud.unfollow_user(db, current_user.id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not following this user"
        )
    
    return {"message": f"You have unfollowed {user.username}"}

@router.get("/users/{user_id}/followers", response_model=List[UserPublic])
async def get_user_followers(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get a user's followers
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    follows = crud.get_user_followers(db, user_id, skip, limit)
    
    # Get the follower users
    followers = []
    for follow in follows:
        follower = crud.get_user(db, follow.follower_id)
        if follower:
            followers.append(follower)
    
    return followers

@router.get("/users/{user_id}/following", response_model=List[UserPublic])
async def get_user_following(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get users that a user is following
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    follows = crud.get_user_following(db, user_id, skip, limit)
    
    # Get the followed users
    following = []
    for follow in follows:
        followed = crud.get_user(db, follow.followed_id)
        if followed:
            following.append(followed)
    
    return following

@router.get("/notifications", response_model=List[Notification])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's notifications
    """
    return crud.get_user_notifications(db, current_user.id, skip, limit)

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    """
    success = crud.mark_notification_read(db, notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all of the current user's notifications as read
    """
    crud.mark_all_notifications_read(db, current_user.id)
    return {"message": "All notifications marked as read"}