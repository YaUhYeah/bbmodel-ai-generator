import os
import json
import time
import uuid
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.core.config import settings

# Mock model generation status storage
MODEL_STATUS = {}

class ModelGenerator:
    def __init__(self):
        os.makedirs(settings.MODELS_DIR, exist_ok=True)
        os.makedirs(settings.TEXTURES_DIR, exist_ok=True)
    
    def get_model_status(self, model_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a model generation task"""
        if model_id not in MODEL_STATUS:
            return None
        
        status = MODEL_STATUS[model_id]
        
        # Add download URL if model is completed
        if status["status"] == "completed":
            status["download_url"] = f"/api/models/{model_id}/download"
        
        return status
    
    async def generate_model(
        self,
        prompt: str,
        model_id: str,
        model_type: str = "character",
        animation_type: Optional[str] = None,
        user_id: str = None,
        db_session = None,
        token_cost: int = 1
    ):
        """Generate a bbmodel based on the prompt"""
        # Update status to processing
        MODEL_STATUS[model_id] = {
            "model_id": model_id,
            "status": "processing",
            "message": "Starting model generation...",
            "token_cost": token_cost
        }
        
        try:
            # If we have a database session, deduct tokens from user
            if db_session and user_id:
                from app.db import crud
                
                # Check if user has enough tokens
                user = crud.get_user(db_session, user_id)
                if user and user.token_balance < token_cost:
                    raise ValueError(f"Insufficient tokens. Required: {token_cost}, Available: {user.token_balance}")
                
                # Deduct tokens
                crud.create_token_transaction(db_session, {
                    "user_id": user_id,
                    "amount": -token_cost,
                    "description": f"Generated model: {prompt[:30]}..."
                })
            
            # Simulate processing time
            MODEL_STATUS[model_id]["message"] = "Analyzing prompt..."
            time.sleep(1)
            
            MODEL_STATUS[model_id]["message"] = "Generating 3D structure..."
            time.sleep(2)
            
            MODEL_STATUS[model_id]["message"] = "Creating textures..."
            time.sleep(1)
            
            if animation_type:
                MODEL_STATUS[model_id]["message"] = f"Adding {animation_type} animations..."
                time.sleep(1)
            
            # Generate a mock bbmodel file
            bbmodel = self._generate_mock_bbmodel(prompt, model_type, animation_type, user_id)
            
            # Save the bbmodel file
            model_path = os.path.join(settings.MODELS_DIR, f"{model_id}.bbmodel")
            with open(model_path, "w") as f:
                json.dump(bbmodel, f, indent=2)
            
            # Update status to completed
            preview_url = f"/static/models/{model_id}_preview.png"
            MODEL_STATUS[model_id] = {
                "model_id": model_id,
                "status": "completed",
                "message": "Model generation completed successfully",
                "preview_url": preview_url,
                "download_url": f"/api/models/{model_id}/download",
                "token_cost": token_cost
            }
            
        except Exception as e:
            # Update status to failed
            MODEL_STATUS[model_id] = {
                "model_id": model_id,
                "status": "failed",
                "message": f"Model generation failed: {str(e)}",
                "token_cost": token_cost
            }
    
    def _generate_mock_bbmodel(
        self,
        prompt: str,
        model_type: str,
        animation_type: Optional[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Generate a mock bbmodel file for demonstration purposes"""
        
        # Create a basic structure based on model_type
        if model_type == "character":
            elements = self._generate_character_elements()
        elif model_type == "animal":
            elements = self._generate_animal_elements()
        elif model_type == "vehicle":
            elements = self._generate_vehicle_elements()
        else:
            elements = self._generate_basic_elements()
        
        # Add animations if requested
        animations = []
        if animation_type:
            animations = self._generate_animations(elements, animation_type)
        
        # Create the bbmodel structure
        bbmodel = {
            "meta": {
                "format_version": "4.5",
                "model_format": "free",
                "box_uv": False
            },
            "name": f"AI Generated: {prompt[:20]}",
            "geometry_name": "",
            "visible_box": [1, 1, 0],
            "variable_placeholders": "",
            "resolution": {
                "width": 64,
                "height": 64
            },
            "elements": elements,
            "outliner": self._generate_outliner(elements),
            "animations": animations,
            "metadata": {
                "prompt": prompt,
                "model_type": model_type,
                "animation_type": animation_type,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "generator": "AI-Powered bbmodel Generator"
            }
        }
        
        return bbmodel
    
    def _generate_character_elements(self) -> List[Dict[str, Any]]:
        """Generate elements for a character model"""
        elements = []
        
        # Head
        head_uuid = str(uuid.uuid4())
        elements.append({
            "name": "head",
            "uuid": head_uuid,
            "type": "cube",
            "from": [-4, 24, -4],
            "to": [4, 32, 4],
            "autouv": 1,
            "color": 0,
            "origin": [0, 24, 0],
            "faces": {
                "north": {"uv": [0, 0, 8, 8], "texture": 0},
                "east": {"uv": [8, 0, 16, 8], "texture": 0},
                "south": {"uv": [16, 0, 24, 8], "texture": 0},
                "west": {"uv": [24, 0, 32, 8], "texture": 0},
                "up": {"uv": [8, 0, 16, 8], "texture": 0},
                "down": {"uv": [16, 0, 24, 8], "texture": 0}
            }
        })
        
        # Body
        body_uuid = str(uuid.uuid4())
        elements.append({
            "name": "body",
            "uuid": body_uuid,
            "type": "cube",
            "from": [-4, 12, -2],
            "to": [4, 24, 2],
            "autouv": 1,
            "color": 1,
            "origin": [0, 12, 0],
            "faces": {
                "north": {"uv": [0, 8, 8, 20], "texture": 0},
                "east": {"uv": [8, 8, 12, 20], "texture": 0},
                "south": {"uv": [12, 8, 20, 20], "texture": 0},
                "west": {"uv": [20, 8, 24, 20], "texture": 0},
                "up": {"uv": [8, 8, 16, 12], "texture": 0},
                "down": {"uv": [16, 8, 24, 12], "texture": 0}
            }
        })
        
        # Left Arm
        left_arm_uuid = str(uuid.uuid4())
        elements.append({
            "name": "left_arm",
            "uuid": left_arm_uuid,
            "type": "cube",
            "from": [4, 12, -2],
            "to": [8, 24, 2],
            "autouv": 1,
            "color": 2,
            "origin": [4, 22, 0],
            "faces": {
                "north": {"uv": [32, 0, 36, 12], "texture": 0},
                "east": {"uv": [36, 0, 40, 12], "texture": 0},
                "south": {"uv": [40, 0, 44, 12], "texture": 0},
                "west": {"uv": [44, 0, 48, 12], "texture": 0},
                "up": {"uv": [32, 0, 36, 4], "texture": 0},
                "down": {"uv": [36, 0, 40, 4], "texture": 0}
            }
        })
        
        # Right Arm
        right_arm_uuid = str(uuid.uuid4())
        elements.append({
            "name": "right_arm",
            "uuid": right_arm_uuid,
            "type": "cube",
            "from": [-8, 12, -2],
            "to": [-4, 24, 2],
            "autouv": 1,
            "color": 3,
            "origin": [-4, 22, 0],
            "faces": {
                "north": {"uv": [48, 0, 52, 12], "texture": 0},
                "east": {"uv": [52, 0, 56, 12], "texture": 0},
                "south": {"uv": [56, 0, 60, 12], "texture": 0},
                "west": {"uv": [60, 0, 64, 12], "texture": 0},
                "up": {"uv": [48, 0, 52, 4], "texture": 0},
                "down": {"uv": [52, 0, 56, 4], "texture": 0}
            }
        })
        
        # Left Leg
        left_leg_uuid = str(uuid.uuid4())
        elements.append({
            "name": "left_leg",
            "uuid": left_leg_uuid,
            "type": "cube",
            "from": [0, 0, -2],
            "to": [4, 12, 2],
            "autouv": 1,
            "color": 4,
            "origin": [0, 12, 0],
            "faces": {
                "north": {"uv": [0, 20, 4, 32], "texture": 0},
                "east": {"uv": [4, 20, 8, 32], "texture": 0},
                "south": {"uv": [8, 20, 12, 32], "texture": 0},
                "west": {"uv": [12, 20, 16, 32], "texture": 0},
                "up": {"uv": [0, 20, 4, 24], "texture": 0},
                "down": {"uv": [4, 20, 8, 24], "texture": 0}
            }
        })
        
        # Right Leg
        right_leg_uuid = str(uuid.uuid4())
        elements.append({
            "name": "right_leg",
            "uuid": right_leg_uuid,
            "type": "cube",
            "from": [-4, 0, -2],
            "to": [0, 12, 2],
            "autouv": 1,
            "color": 5,
            "origin": [0, 12, 0],
            "faces": {
                "north": {"uv": [16, 20, 20, 32], "texture": 0},
                "east": {"uv": [20, 20, 24, 32], "texture": 0},
                "south": {"uv": [24, 20, 28, 32], "texture": 0},
                "west": {"uv": [28, 20, 32, 32], "texture": 0},
                "up": {"uv": [16, 20, 20, 24], "texture": 0},
                "down": {"uv": [20, 20, 24, 24], "texture": 0}
            }
        })
        
        return elements
    
    def _generate_animal_elements(self) -> List[Dict[str, Any]]:
        """Generate elements for an animal model"""
        elements = []
        
        # Body
        body_uuid = str(uuid.uuid4())
        elements.append({
            "name": "body",
            "uuid": body_uuid,
            "type": "cube",
            "from": [-4, 8, -8],
            "to": [4, 16, 8],
            "autouv": 1,
            "color": 0,
            "origin": [0, 12, 0],
            "faces": {
                "north": {"uv": [0, 0, 8, 8], "texture": 0},
                "east": {"uv": [8, 0, 24, 8], "texture": 0},
                "south": {"uv": [24, 0, 32, 8], "texture": 0},
                "west": {"uv": [32, 0, 48, 8], "texture": 0},
                "up": {"uv": [0, 8, 8, 24], "texture": 0},
                "down": {"uv": [8, 8, 16, 24], "texture": 0}
            }
        })
        
        # Head
        head_uuid = str(uuid.uuid4())
        elements.append({
            "name": "head",
            "uuid": head_uuid,
            "type": "cube",
            "from": [-3, 9, 8],
            "to": [3, 15, 14],
            "autouv": 1,
            "color": 1,
            "origin": [0, 12, 8],
            "faces": {
                "north": {"uv": [16, 8, 22, 14], "texture": 0},
                "east": {"uv": [22, 8, 28, 14], "texture": 0},
                "south": {"uv": [28, 8, 34, 14], "texture": 0},
                "west": {"uv": [34, 8, 40, 14], "texture": 0},
                "up": {"uv": [16, 14, 22, 20], "texture": 0},
                "down": {"uv": [22, 14, 28, 20], "texture": 0}
            }
        })
        
        # Legs
        for i in range(4):
            x_offset = -3 if i % 2 == 0 else 1
            z_offset = -6 if i < 2 else 4
            leg_uuid = str(uuid.uuid4())
            elements.append({
                "name": f"leg_{i+1}",
                "uuid": leg_uuid,
                "type": "cube",
                "from": [x_offset, 0, z_offset],
                "to": [x_offset + 2, 8, z_offset + 2],
                "autouv": 1,
                "color": i + 2,
                "origin": [x_offset + 1, 4, z_offset + 1],
                "faces": {
                    "north": {"uv": [40, i*8, 42, i*8+8], "texture": 0},
                    "east": {"uv": [42, i*8, 44, i*8+8], "texture": 0},
                    "south": {"uv": [44, i*8, 46, i*8+8], "texture": 0},
                    "west": {"uv": [46, i*8, 48, i*8+8], "texture": 0},
                    "up": {"uv": [40, i*8, 42, i*8+2], "texture": 0},
                    "down": {"uv": [42, i*8, 44, i*8+2], "texture": 0}
                }
            })
        
        # Tail
        tail_uuid = str(uuid.uuid4())
        elements.append({
            "name": "tail",
            "uuid": tail_uuid,
            "type": "cube",
            "from": [-1, 10, -12],
            "to": [1, 14, -8],
            "autouv": 1,
            "color": 6,
            "origin": [0, 12, -8],
            "faces": {
                "north": {"uv": [48, 0, 50, 4], "texture": 0},
                "east": {"uv": [50, 0, 54, 4], "texture": 0},
                "south": {"uv": [54, 0, 56, 4], "texture": 0},
                "west": {"uv": [56, 0, 60, 4], "texture": 0},
                "up": {"uv": [48, 4, 50, 8], "texture": 0},
                "down": {"uv": [50, 4, 52, 8], "texture": 0}
            }
        })
        
        return elements
    
    def _generate_vehicle_elements(self) -> List[Dict[str, Any]]:
        """Generate elements for a vehicle model"""
        elements = []
        
        # Main body
        body_uuid = str(uuid.uuid4())
        elements.append({
            "name": "body",
            "uuid": body_uuid,
            "type": "cube",
            "from": [-8, 0, -12],
            "to": [8, 6, 12],
            "autouv": 1,
            "color": 0,
            "origin": [0, 0, 0],
            "faces": {
                "north": {"uv": [0, 0, 16, 6], "texture": 0},
                "east": {"uv": [16, 0, 40, 6], "texture": 0},
                "south": {"uv": [40, 0, 56, 6], "texture": 0},
                "west": {"uv": [0, 6, 24, 12], "texture": 0},
                "up": {"uv": [0, 12, 16, 36], "texture": 0},
                "down": {"uv": [16, 12, 32, 36], "texture": 0}
            }
        })
        
        # Cabin
        cabin_uuid = str(uuid.uuid4())
        elements.append({
            "name": "cabin",
            "uuid": cabin_uuid,
            "type": "cube",
            "from": [-6, 6, -4],
            "to": [6, 12, 6],
            "autouv": 1,
            "color": 1,
            "origin": [0, 6, 0],
            "faces": {
                "north": {"uv": [24, 6, 36, 12], "texture": 0},
                "east": {"uv": [36, 6, 46, 12], "texture": 0},
                "south": {"uv": [46, 6, 58, 12], "texture": 0},
                "west": {"uv": [32, 12, 42, 18], "texture": 0},
                "up": {"uv": [32, 18, 44, 28], "texture": 0},
                "down": {"uv": [44, 18, 56, 28], "texture": 0}
            }
        })
        
        # Wheels
        wheel_positions = [
            [-7, -3, -8],
            [7, -3, -8],
            [-7, -3, 8],
            [7, -3, 8]
        ]
        
        for i, pos in enumerate(wheel_positions):
            wheel_uuid = str(uuid.uuid4())
            elements.append({
                "name": f"wheel_{i+1}",
                "uuid": wheel_uuid,
                "type": "cube",
                "from": [pos[0] - 2, pos[1] - 2, pos[2] - 2],
                "to": [pos[0] + 2, pos[1] + 2, pos[2] + 2],
                "autouv": 1,
                "color": i + 2,
                "origin": pos,
                "faces": {
                    "north": {"uv": [56, i*8, 60, i*8+4], "texture": 0},
                    "east": {"uv": [56, i*8+4, 60, i*8+8], "texture": 0},
                    "south": {"uv": [60, i*8, 64, i*8+4], "texture": 0},
                    "west": {"uv": [60, i*8+4, 64, i*8+8], "texture": 0},
                    "up": {"uv": [56, i*8+8, 60, i*8+12], "texture": 0},
                    "down": {"uv": [60, i*8+8, 64, i*8+12], "texture": 0}
                }
            })
        
        return elements
    
    def _generate_basic_elements(self) -> List[Dict[str, Any]]:
        """Generate basic cube elements"""
        elements = []
        
        # Create a simple cube
        cube_uuid = str(uuid.uuid4())
        elements.append({
            "name": "cube",
            "uuid": cube_uuid,
            "type": "cube",
            "from": [-8, 0, -8],
            "to": [8, 16, 8],
            "autouv": 1,
            "color": 0,
            "origin": [0, 0, 0],
            "faces": {
                "north": {"uv": [0, 0, 16, 16], "texture": 0},
                "east": {"uv": [16, 0, 32, 16], "texture": 0},
                "south": {"uv": [32, 0, 48, 16], "texture": 0},
                "west": {"uv": [48, 0, 64, 16], "texture": 0},
                "up": {"uv": [0, 16, 16, 32], "texture": 0},
                "down": {"uv": [16, 16, 32, 32], "texture": 0}
            }
        })
        
        return elements
    
    def _generate_outliner(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate the outliner structure based on elements"""
        outliner = []
        
        for element in elements:
            outliner.append({
                "uuid": element["uuid"],
                "name": element["name"]
            })
        
        return outliner
    
    def _generate_animations(
        self,
        elements: List[Dict[str, Any]],
        animation_type: str
    ) -> List[Dict[str, Any]]:
        """Generate animations based on the elements and animation type"""
        animations = []
        
        if animation_type == "walk":
            animations.append(self._generate_walk_animation(elements))
        elif animation_type == "idle":
            animations.append(self._generate_idle_animation(elements))
        elif animation_type == "attack":
            animations.append(self._generate_attack_animation(elements))
        
        return animations
    
    def _generate_walk_animation(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a walking animation"""
        animators = {}
        
        for element in elements:
            if "leg" in element["name"] or "arm" in element["name"]:
                # Create swinging animation for limbs
                animators[element["uuid"]] = {
                    "rotation": {
                        "0": [0, 0, 0],
                        "0.25": [30, 0, 0],
                        "0.5": [0, 0, 0],
                        "0.75": [-30, 0, 0],
                        "1": [0, 0, 0]
                    }
                }
            elif "body" in element["name"]:
                # Slight body movement
                animators[element["uuid"]] = {
                    "position": {
                        "0": [0, 0, 0],
                        "0.5": [0, 0.5, 0],
                        "1": [0, 0, 0]
                    }
                }
            elif "head" in element["name"]:
                # Head bobbing
                animators[element["uuid"]] = {
                    "rotation": {
                        "0": [0, 0, 0],
                        "0.5": [5, 0, 0],
                        "1": [0, 0, 0]
                    }
                }
        
        return {
            "name": "walk",
            "uuid": str(uuid.uuid4()),
            "loop": "loop",
            "override": False,
            "length": 1,
            "snapping": 24,
            "selected": False,
            "animators": animators
        }
    
    def _generate_idle_animation(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an idle animation"""
        animators = {}
        
        for element in elements:
            if "head" in element["name"]:
                # Head looking around
                animators[element["uuid"]] = {
                    "rotation": {
                        "0": [0, 0, 0],
                        "1": [0, 15, 0],
                        "2": [0, 0, 0],
                        "3": [0, -15, 0],
                        "4": [0, 0, 0]
                    }
                }
            elif "body" in element["name"]:
                # Breathing motion
                animators[element["uuid"]] = {
                    "scale": {
                        "0": [1, 1, 1],
                        "1": [1, 1.03, 1],
                        "2": [1, 1, 1]
                    }
                }
            elif "arm" in element["name"]:
                # Slight arm movement
                animators[element["uuid"]] = {
                    "rotation": {
                        "0": [0, 0, 0],
                        "2": [5, 0, 0],
                        "4": [0, 0, 0]
                    }
                }
        
        return {
            "name": "idle",
            "uuid": str(uuid.uuid4()),
            "loop": "loop",
            "override": False,
            "length": 4,
            "snapping": 24,
            "selected": False,
            "animators": animators
        }
    
    def _generate_attack_animation(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an attack animation"""
        animators = {}
        
        for element in elements:
            if "arm" in element["name"] and "right" in element["name"]:
                # Swinging arm
                animators[element["uuid"]] = {
                    "rotation": {
                        "0": [0, 0, 0],
                        "0.1": [-90, 0, 0],
                        "0.2": [-180, 0, 0],
                        "0.5": [0, 0, 0]
                    }
                }
            elif "body" in element["name"]:
                # Body twist
                animators[element["uuid"]] = {
                    "rotation": {
                        "0": [0, 0, 0],
                        "0.1": [0, -20, 0],
                        "0.3": [0, 0, 0]
                    }
                }
            elif "head" in element["name"]:
                # Head follows the attack
                animators[element["uuid"]] = {
                    "rotation": {
                        "0": [0, 0, 0],
                        "0.1": [0, -15, 0],
                        "0.3": [0, 0, 0]
                    }
                }
        
        return {
            "name": "attack",
            "uuid": str(uuid.uuid4()),
            "loop": "once",
            "override": False,
            "length": 0.5,
            "snapping": 24,
            "selected": False,
            "animators": animators
        }