from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from app.db.models import User, UserProfile, Subscription, SubscriptionTier, UserRole
from app.services.auth import get_password_hash

logger = logging.getLogger(__name__)

# Initial subscription plans
SUBSCRIPTION_PLANS = [
    {
        "tier": SubscriptionTier.BASIC,
        "tokens_per_month": 50,
        "price_monthly": 9.99,
        "price_yearly": 99.99,
        "features": [
            "50 tokens per month",
            "Basic model types",
            "Standard animations",
            "Community access"
        ]
    },
    {
        "tier": SubscriptionTier.PRO,
        "tokens_per_month": 200,
        "price_monthly": 24.99,
        "price_yearly": 249.99,
        "features": [
            "200 tokens per month",
            "All model types",
            "Advanced animations",
            "Priority support",
            "Commercial usage"
        ]
    },
    {
        "tier": SubscriptionTier.ENTERPRISE,
        "tokens_per_month": 1000,
        "price_monthly": 99.99,
        "price_yearly": 999.99,
        "features": [
            "1000 tokens per month",
            "All features",
            "Custom animations",
            "Dedicated support",
            "API access",
            "Team collaboration"
        ]
    }
]

def init_db(db: Session) -> None:
    """Initialize the database with default data"""
    # Create admin user if it doesn't exist
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("password"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
            role=UserRole.ADMIN,
            token_balance=1000  # Give admin plenty of tokens
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Create admin profile
        admin_profile = UserProfile(
            user_id=admin_user.id,
            bio="System administrator",
            avatar_url="https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        )
        db.add(admin_profile)
        db.commit()
        
        logger.info("Admin user created")
    
    # Create subscription plans if they don't exist
    for plan_data in SUBSCRIPTION_PLANS:
        plan = db.query(Subscription).filter(
            Subscription.tier == plan_data["tier"]
        ).first()
        
        if not plan:
            plan = Subscription(**plan_data)
            db.add(plan)
            db.commit()
            logger.info(f"Created subscription plan: {plan_data['tier'].value}")
    
    logger.info("Database initialization completed")