from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any

from app.db.models import (
    User, UserProfile, Model, Tag, Subscription, UserSubscription, 
    TokenTransaction, Like, Comment, Follow, Notification,
    VisibilityType, ModelStatus, NotificationType
)
from app.utils.password import get_password_hash

# User CRUD operations
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: str) -> Optional[User]:
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_data: Dict[str, Any]) -> User:
    """Create a new user"""
    hashed_password = user_data.pop("hashed_password", None)
    password = user_data.pop("password", None)
    
    if password and not hashed_password:
        hashed_password = get_password_hash(password)
    
    user = User(
        id=str(uuid.uuid4()),
        hashed_password=hashed_password,
        **user_data
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        avatar_url="https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
    )
    db.add(profile)
    db.commit()
    
    return user

def update_user(db: Session, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
    """Update a user"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    # Handle password separately
    password = user_data.pop("password", None)
    if password:
        user.hashed_password = get_password_hash(password)
    
    # Update profile data if provided
    profile_data = user_data.pop("profile", None)
    if profile_data and user.profile:
        for key, value in profile_data.items():
            setattr(user.profile, key, value)
    
    # Update user attributes
    for key, value in user_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get a list of users"""
    return db.query(User).offset(skip).limit(limit).all()

def delete_user(db: Session, user_id: str) -> bool:
    """Delete a user"""
    user = get_user(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True

# Model CRUD operations
def create_model(db: Session, model_data: Dict[str, Any]) -> Model:
    """Create a new model"""
    # Handle tags
    tags_data = model_data.pop("tags", [])
    
    model = Model(
        id=str(uuid.uuid4()),
        **model_data
    )
    db.add(model)
    db.commit()
    
    # Add tags
    if tags_data:
        for tag_name in tags_data:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(id=str(uuid.uuid4()), name=tag_name)
                db.add(tag)
                db.commit()
            
            model.tags.append(tag)
        
        db.commit()
    
    db.refresh(model)
    return model

def get_model(db: Session, model_id: str) -> Optional[Model]:
    """Get a model by ID"""
    return db.query(Model).filter(Model.id == model_id).first()

def get_models_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Model]:
    """Get models by user ID"""
    return db.query(Model).filter(Model.user_id == user_id).offset(skip).limit(limit).all()

def get_public_models(db: Session, skip: int = 0, limit: int = 20, search: Optional[str] = None) -> List[Model]:
    """Get public models with optional search"""
    query = db.query(Model).filter(Model.visibility == VisibilityType.PUBLIC)
    
    if search:
        search_term = f"%{search}%"
        query = query.join(Model.tags).filter(
            or_(
                Model.name.ilike(search_term),
                Model.prompt.ilike(search_term),
                Tag.name.ilike(search_term)
            )
        ).distinct()
    
    return query.order_by(desc(Model.created_at)).offset(skip).limit(limit).all()

def update_model(db: Session, model_id: str, model_data: Dict[str, Any]) -> Optional[Model]:
    """Update a model"""
    model = get_model(db, model_id)
    if not model:
        return None
    
    # Handle tags separately
    tags_data = model_data.pop("tags", None)
    if tags_data is not None:
        # Clear existing tags
        model.tags = []
        
        # Add new tags
        for tag_name in tags_data:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(id=str(uuid.uuid4()), name=tag_name)
                db.add(tag)
                db.commit()
            
            model.tags.append(tag)
    
    # Update model attributes
    for key, value in model_data.items():
        setattr(model, key, value)
    
    db.commit()
    db.refresh(model)
    return model

def delete_model(db: Session, model_id: str) -> bool:
    """Delete a model"""
    model = get_model(db, model_id)
    if not model:
        return False
    
    db.delete(model)
    db.commit()
    return True

def increment_model_view(db: Session, model_id: str) -> bool:
    """Increment model view count"""
    model = get_model(db, model_id)
    if not model:
        return False
    
    model.view_count += 1
    db.commit()
    return True

def increment_model_download(db: Session, model_id: str) -> bool:
    """Increment model download count"""
    model = get_model(db, model_id)
    if not model:
        return False
    
    model.download_count += 1
    db.commit()
    return True

# Subscription CRUD operations
def get_subscription_plans(db: Session) -> List[Subscription]:
    """Get all subscription plans"""
    return db.query(Subscription).all()

def get_subscription(db: Session, subscription_id: str) -> Optional[Subscription]:
    """Get a subscription by ID"""
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()

def get_user_subscription(db: Session, user_id: str) -> Optional[UserSubscription]:
    """Get a user's active subscription"""
    return db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active == True
    ).first()

def create_user_subscription(db: Session, subscription_data: Dict[str, Any]) -> UserSubscription:
    """Create a user subscription"""
    user_sub = UserSubscription(
        id=str(uuid.uuid4()),
        **subscription_data
    )
    db.add(user_sub)
    db.commit()
    db.refresh(user_sub)
    return user_sub

def cancel_user_subscription(db: Session, user_id: str) -> bool:
    """Cancel a user's subscription"""
    user_sub = get_user_subscription(db, user_id)
    if not user_sub:
        return False
    
    user_sub.is_active = False
    db.commit()
    return True

# Token transaction CRUD operations
def create_token_transaction(db: Session, transaction_data: Dict[str, Any]) -> TokenTransaction:
    """Create a token transaction"""
    transaction = TokenTransaction(
        id=str(uuid.uuid4()),
        **transaction_data
    )
    db.add(transaction)
    
    # Update user's token balance
    user = get_user(db, transaction_data["user_id"])
    if user:
        user.token_balance += transaction_data["amount"]
    
    db.commit()
    db.refresh(transaction)
    return transaction

def get_user_token_transactions(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[TokenTransaction]:
    """Get a user's token transactions"""
    return db.query(TokenTransaction).filter(
        TokenTransaction.user_id == user_id
    ).order_by(desc(TokenTransaction.created_at)).offset(skip).limit(limit).all()

# Social features CRUD operations
def like_model(db: Session, user_id: str, model_id: str) -> Like:
    """Like a model"""
    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.user_id == user_id,
        Like.model_id == model_id
    ).first()
    
    if existing_like:
        return existing_like
    
    # Create new like
    like = Like(
        id=str(uuid.uuid4()),
        user_id=user_id,
        model_id=model_id
    )
    db.add(like)
    
    # Update model like count
    model = get_model(db, model_id)
    if model:
        model.like_count += 1
    
    db.commit()
    db.refresh(like)
    
    # Create notification for model owner
    if model and model.user_id != user_id:
        user = get_user(db, user_id)
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=model.user_id,
            type=NotificationType.LIKE,
            content=f"{user.username} liked your model '{model.name}'",
            related_id=model_id
        )
        db.add(notification)
        db.commit()
    
    return like

def unlike_model(db: Session, user_id: str, model_id: str) -> bool:
    """Unlike a model"""
    like = db.query(Like).filter(
        Like.user_id == user_id,
        Like.model_id == model_id
    ).first()
    
    if not like:
        return False
    
    db.delete(like)
    
    # Update model like count
    model = get_model(db, model_id)
    if model and model.like_count > 0:
        model.like_count -= 1
    
    db.commit()
    return True

def add_comment(db: Session, comment_data: Dict[str, Any]) -> Comment:
    """Add a comment to a model"""
    comment = Comment(
        id=str(uuid.uuid4()),
        **comment_data
    )
    db.add(comment)
    
    # Update model comment count
    model = get_model(db, comment_data["model_id"])
    if model:
        model.comment_count += 1
    
    db.commit()
    db.refresh(comment)
    
    # Create notification for model owner
    if model and model.user_id != comment_data["user_id"]:
        user = get_user(db, comment_data["user_id"])
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=model.user_id,
            type=NotificationType.COMMENT,
            content=f"{user.username} commented on your model '{model.name}'",
            related_id=model_id
        )
        db.add(notification)
        db.commit()
    
    return comment

def get_model_comments(db: Session, model_id: str, skip: int = 0, limit: int = 50) -> List[Comment]:
    """Get comments for a model"""
    return db.query(Comment).filter(
        Comment.model_id == model_id
    ).order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()

def follow_user(db: Session, follower_id: str, followed_id: str) -> Follow:
    """Follow a user"""
    # Check if already following
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == follower_id,
        Follow.followed_id == followed_id
    ).first()
    
    if existing_follow:
        return existing_follow
    
    # Create new follow
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=follower_id,
        followed_id=followed_id
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    
    # Create notification
    follower = get_user(db, follower_id)
    notification = Notification(
        id=str(uuid.uuid4()),
        user_id=followed_id,
        type=NotificationType.FOLLOW,
        content=f"{follower.username} started following you",
        related_id=follower_id
    )
    db.add(notification)
    db.commit()
    
    return follow

def unfollow_user(db: Session, follower_id: str, followed_id: str) -> bool:
    """Unfollow a user"""
    follow = db.query(Follow).filter(
        Follow.follower_id == follower_id,
        Follow.followed_id == followed_id
    ).first()
    
    if not follow:
        return False
    
    db.delete(follow)
    db.commit()
    return True

def get_user_followers(db: Session, user_id: str, skip: int = 0, limit: int = 50) -> List[Follow]:
    """Get a user's followers"""
    return db.query(Follow).filter(
        Follow.followed_id == user_id
    ).offset(skip).limit(limit).all()

def get_user_following(db: Session, user_id: str, skip: int = 0, limit: int = 50) -> List[Follow]:
    """Get users that a user is following"""
    return db.query(Follow).filter(
        Follow.follower_id == user_id
    ).offset(skip).limit(limit).all()

def get_user_notifications(db: Session, user_id: str, skip: int = 0, limit: int = 50) -> List[Notification]:
    """Get a user's notifications"""
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

def mark_notification_read(db: Session, notification_id: str) -> bool:
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        return False
    
    notification.is_read = True
    db.commit()
    return True

def mark_all_notifications_read(db: Session, user_id: str) -> bool:
    """Mark all of a user's notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    return True