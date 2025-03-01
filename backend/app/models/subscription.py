from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionBase(BaseModel):
    tier: SubscriptionTier
    tokens_per_month: int
    price_monthly: float
    price_yearly: float
    features: List[str]

class SubscriptionCreate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase):
    id: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class UserSubscriptionBase(BaseModel):
    user_id: str
    subscription_id: str
    is_active: bool = True
    tokens_remaining: int
    renewal_date: datetime
    payment_method_id: Optional[str] = None
    is_yearly: bool = False

class UserSubscriptionCreate(UserSubscriptionBase):
    pass

class UserSubscription(UserSubscriptionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class TokenTransaction(BaseModel):
    id: str
    user_id: str
    amount: int  # Positive for purchases, negative for usage
    description: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class TokenPurchase(BaseModel):
    user_id: str
    amount: int
    payment_method_id: str
    
    model_config = {
        "from_attributes": True
    }