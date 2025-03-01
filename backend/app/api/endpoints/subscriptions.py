from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.base import get_db
from app.db import crud
from app.models.subscription import Subscription, UserSubscription, TokenTransaction
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/plans", response_model=List[Subscription])
async def get_subscription_plans(db: Session = Depends(get_db)):
    """
    Get all available subscription plans
    """
    return crud.get_subscription_plans(db)

@router.get("/my-subscription", response_model=UserSubscription)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's active subscription
    """
    subscription = crud.get_user_subscription(db, current_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't have an active subscription"
        )
    return subscription

@router.post("/subscribe/{subscription_id}", response_model=UserSubscription)
async def subscribe(
    subscription_id: str,
    is_yearly: bool = False,
    payment_method_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subscribe to a plan
    """
    # Check if user already has an active subscription
    existing_sub = crud.get_user_subscription(db, current_user.id)
    if existing_sub and existing_sub.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active subscription. Please cancel it first."
        )
    
    # Get the subscription plan
    subscription = crud.get_subscription(db, subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Calculate renewal date
    renewal_date = datetime.utcnow() + timedelta(days=365 if is_yearly else 30)
    
    # Create user subscription
    user_subscription = crud.create_user_subscription(db, {
        "user_id": current_user.id,
        "subscription_id": subscription_id,
        "is_active": True,
        "tokens_remaining": subscription.tokens_per_month,
        "renewal_date": renewal_date,
        "payment_method_id": payment_method_id,
        "is_yearly": is_yearly
    })
    
    # Add tokens to user's balance
    crud.create_token_transaction(db, {
        "user_id": current_user.id,
        "amount": subscription.tokens_per_month,
        "description": f"Initial tokens from {subscription.tier.value} subscription"
    })
    
    return user_subscription

@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel the current user's subscription
    """
    success = crud.cancel_user_subscription(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return {"message": "Subscription cancelled successfully"}

@router.get("/tokens/history", response_model=List[TokenTransaction])
async def get_token_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's token transaction history
    """
    return crud.get_user_token_transactions(db, current_user.id, skip, limit)

@router.post("/tokens/purchase", response_model=TokenTransaction)
async def purchase_tokens(
    amount: int,
    payment_method_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Purchase additional tokens
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )
    
    # In a real implementation, this would process the payment
    # For now, we'll just add the tokens
    
    transaction = crud.create_token_transaction(db, {
        "user_id": current_user.id,
        "amount": amount,
        "description": f"Purchased {amount} tokens"
    })
    
    return transaction