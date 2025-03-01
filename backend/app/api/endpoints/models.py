from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from fastapi.responses import FileResponse
from typing import List, Optional
import uuid
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.model_generator import ModelGenerator
from app.services.auth import get_current_user
from app.models.user import User
from app.models.bbmodel import BBModelCreate, BBModel, BBModelResponse, ModelStatus, ModelType, AnimationType
from app.models.social import VisibilityType
from app.db.base import get_db
from app.db import crud

router = APIRouter()
model_generator = ModelGenerator()

@router.post("/generate", response_model=BBModelResponse)
async def generate_model(
    prompt: str = Form(...),
    model_type: str = Form("character"),
    animation_type: Optional[str] = Form(None),
    visibility: VisibilityType = Form(VisibilityType.PRIVATE),
    tags: List[str] = Form([]),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new bbmodel based on the provided prompt
    """
    # Calculate token cost based on complexity
    token_cost = 1  # Base cost
    
    if animation_type:
        token_cost += 1  # Additional cost for animations
    
    if model_type in ["environment", "vehicle"]:
        token_cost += 1  # Additional cost for complex models
    
    # Check if user has enough tokens
    if current_user.token_balance < token_cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient tokens. Required: {token_cost}, Available: {current_user.token_balance}"
        )
    
    model_id = str(uuid.uuid4())
    
    # Create model record in database
    model_data = {
        "id": model_id,
        "name": f"Model from: {prompt[:20]}...",
        "prompt": prompt,
        "user_id": current_user.id,
        "status": ModelStatus.PROCESSING,
        "model_type": model_type,
        "animation_type": animation_type,
        "visibility": visibility,
        "tags": tags,
        "token_cost": token_cost
    }
    
    crud.create_model(db, model_data)
    
    # Create a task to generate the model in the background
    background_tasks.add_task(
        model_generator.generate_model,
        prompt=prompt,
        model_id=model_id,
        model_type=model_type,
        animation_type=animation_type,
        user_id=current_user.id,
        db_session=db,
        token_cost=token_cost
    )
    
    return {
        "model_id": model_id,
        "status": ModelStatus.PROCESSING,
        "message": "Model generation started. Check status endpoint for updates.",
        "token_cost": token_cost
    }

@router.get("/status/{model_id}", response_model=BBModelResponse)
async def get_model_status(
    model_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a model generation task
    """
    status = model_generator.get_model_status(model_id, current_user.id)
    if not status:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return status

@router.get("/{model_id}/download")
async def download_model(
    model_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download the generated bbmodel file
    """
    model_path = os.path.join(settings.MODELS_DIR, f"{model_id}.bbmodel")
    
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model file not found")
    
    return FileResponse(
        model_path,
        media_type="application/octet-stream",
        filename=f"{model_id}.bbmodel"
    )

@router.get("/", response_model=List[BBModel])
async def list_models(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    List all models created by the current user
    """
    # In a real implementation, this would query the database
    # For now, we'll scan the models directory
    models = []
    
    for filename in os.listdir(settings.MODELS_DIR):
        if filename.endswith(".bbmodel"):
            model_id = filename.split(".")[0]
            model_path = os.path.join(settings.MODELS_DIR, filename)
            
            try:
                with open(model_path, "r") as f:
                    model_data = json.load(f)
                    
                    # Extract metadata if available
                    metadata = model_data.get("metadata", {})
                    
                    models.append({
                        "id": model_id,
                        "name": metadata.get("name", f"Model {model_id[:8]}"),
                        "prompt": metadata.get("prompt", ""),
                        "created_at": metadata.get("created_at", datetime.now().isoformat()),
                        "user_id": metadata.get("user_id", current_user.id),
                        "status": "completed"
                    })
            except:
                # If we can't read the file, skip it
                continue
    
    # Filter by user_id and apply pagination
    user_models = [m for m in models if m["user_id"] == current_user.id]
    return user_models[skip:skip+limit]