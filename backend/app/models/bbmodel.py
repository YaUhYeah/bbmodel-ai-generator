from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.social import VisibilityType

class ModelType(str, Enum):
    CHARACTER = "character"
    ANIMAL = "animal"
    VEHICLE = "vehicle"
    PROP = "prop"
    ENVIRONMENT = "environment"
    CUSTOM = "custom"

class AnimationType(str, Enum):
    NONE = "none"
    WALK = "walk"
    IDLE = "idle"
    ATTACK = "attack"
    CUSTOM = "custom"

class ModelStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BBModelCreate(BaseModel):
    prompt: str
    model_type: ModelType = ModelType.CHARACTER
    animation_type: Optional[AnimationType] = None
    visibility: VisibilityType = VisibilityType.PRIVATE
    tags: List[str] = []
    token_cost: int = 1  # Default token cost

class BBModel(BaseModel):
    id: str
    name: str
    prompt: str
    created_at: datetime
    user_id: str
    status: ModelStatus
    preview_url: Optional[str] = None
    model_type: ModelType
    animation_type: Optional[AnimationType] = None
    visibility: VisibilityType = VisibilityType.PRIVATE
    tags: List[str] = []
    like_count: int = 0
    comment_count: int = 0
    view_count: int = 0
    download_count: int = 0
    token_cost: int = 1
    
    model_config = {
        "from_attributes": True
    }

class BBModelResponse(BaseModel):
    model_id: str
    status: ModelStatus
    message: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    token_cost: int = 1
    
    model_config = {
        "from_attributes": True
    }

class BBModelPublic(BaseModel):
    id: str
    name: str
    prompt: str
    created_at: datetime
    user_id: str
    username: str  # Creator's username
    preview_url: Optional[str] = None
    model_type: ModelType
    animation_type: Optional[AnimationType] = None
    tags: List[str] = []
    like_count: int = 0
    comment_count: int = 0
    view_count: int = 0
    download_count: int = 0
    
    model_config = {
        "from_attributes": True
    }

class BBModelElement(BaseModel):
    uuid: str
    type: str
    name: str
    origin: List[float] = [0, 0, 0]
    rotation: List[float] = [0, 0, 0]
    vertices: Optional[List[List[float]]] = None
    faces: Optional[List[List[int]]] = None
    
    model_config = {
        "from_attributes": True
    }

class BBModelAnimation(BaseModel):
    name: str
    uuid: str
    loop: str = "once"
    length: float
    snapping: int = 24
    animators: Dict[str, Any]
    
    model_config = {
        "from_attributes": True
    }

class BBModelFile(BaseModel):
    meta: Dict[str, Any]
    name: str
    model_format: str = "free"
    box_uv: bool = False
    texture_width: int = 64
    texture_height: int = 64
    elements: List[BBModelElement]
    outliner: List[Dict[str, Any]]
    animations: List[BBModelAnimation] = []
    resolution: Dict[str, int]
    
    model_config = {
        "from_attributes": True
    }