from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, JSON, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base

# Association table for model tags
model_tags = Table(
    "model_tags",
    Base.metadata,
    Column("model_id", String, ForeignKey("models.id")),
    Column("tag_id", String, ForeignKey("tags.id"))
)

class VisibilityType(enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    UNLISTED = "unlisted"

class ModelType(enum.Enum):
    CHARACTER = "character"
    ANIMAL = "animal"
    VEHICLE = "vehicle"
    PROP = "prop"
    ENVIRONMENT = "environment"
    CUSTOM = "custom"

class AnimationType(enum.Enum):
    NONE = "none"
    WALK = "walk"
    IDLE = "idle"
    ATTACK = "attack"
    CUSTOM = "custom"

class ModelStatus(enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UserRole(enum.Enum):
    USER = "user"
    CREATOR = "creator"
    MODERATOR = "moderator"
    ADMIN = "admin"

class SubscriptionTier(enum.Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class NotificationType(enum.Enum):
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    SYSTEM = "system"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    token_balance = Column(Integer, default=0)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    models = relationship("Model", back_populates="user")
    subscriptions = relationship("UserSubscription", back_populates="user")
    token_transactions = relationship("TokenTransaction", back_populates="user")
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    followers = relationship("Follow", foreign_keys="Follow.followed_id", back_populates="followed")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    website = Column(String, nullable=True)
    social_links = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")

class Model(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    prompt = Column(Text)
    user_id = Column(String, ForeignKey("users.id"))
    status = Column(Enum(ModelStatus), default=ModelStatus.PROCESSING)
    preview_url = Column(String, nullable=True)
    model_type = Column(Enum(ModelType), default=ModelType.CHARACTER)
    animation_type = Column(Enum(AnimationType), nullable=True)
    visibility = Column(Enum(VisibilityType), default=VisibilityType.PRIVATE)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    token_cost = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="models")
    likes = relationship("Like", back_populates="model")
    comments = relationship("Comment", back_populates="model")
    tags = relationship("Tag", secondary=model_tags, back_populates="models")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    models = relationship("Model", secondary=model_tags, back_populates="tags")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    tier = Column(Enum(SubscriptionTier))
    tokens_per_month = Column(Integer)
    price_monthly = Column(Float)
    price_yearly = Column(Float)
    features = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_subscriptions = relationship("UserSubscription", back_populates="subscription")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    subscription_id = Column(String, ForeignKey("subscriptions.id"))
    is_active = Column(Boolean, default=True)
    tokens_remaining = Column(Integer)
    renewal_date = Column(DateTime)
    payment_method_id = Column(String, nullable=True)
    is_yearly = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    subscription = relationship("Subscription", back_populates="user_subscriptions")

class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    amount = Column(Integer)  # Positive for purchases, negative for usage
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="token_transactions")

class Like(Base):
    __tablename__ = "likes"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    model_id = Column(String, ForeignKey("models.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="likes")
    model = relationship("Model", back_populates="likes")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    model_id = Column(String, ForeignKey("models.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    model = relationship("Model", back_populates="comments")

class Follow(Base):
    __tablename__ = "follows"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    follower_id = Column(String, ForeignKey("users.id"))
    followed_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    type = Column(Enum(NotificationType))
    content = Column(Text)
    related_id = Column(String, nullable=True)  # ID of the related model, comment, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")