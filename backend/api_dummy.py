# --- Subscription and Payment Routes (Dummy implementations) ---

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, condecimal
from typing import Optional

# These routes are for compatibility with the frontend
# They don't perform any real subscription or payment operations

router = APIRouter()

# --- Dummy Model Classes ---

class SubscriptionResponse(BaseModel):
    subscription_id: int = 1
    user_id: int
    plan_name: str = "free"
    start_date: str
    end_date: Optional[str] = None
    auto_renew: bool = False

class SubscriptionCreate(BaseModel):
    plan_name: str = Field(..., pattern="^(free|basic|pro)$")
    end_date: Optional[str] = None
    auto_renew: bool = False

class SubscriptionUpdate(BaseModel):
    plan_name: Optional[str] = Field(None, pattern="^(free|basic|pro)$")
    end_date: Optional[str] = None
    auto_renew: Optional[bool] = None

class PlanInfo(BaseModel):
    plan_id: str
    name: str
    price: int
    features: List[str]

class PaymentCreate(BaseModel):
    plan_id: str
    currency: str = "INR"

class PaymentVerify(BaseModel):
    order_id: str
    payment_id: str
    signature: str

class OrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str

class VerifyResponse(BaseModel):
    success: bool
    message: str
    subscription: Dict[str, Any]

# --- Subscription Routes ---

@router.get("/subscriptions/plans", response_model=List[PlanInfo])
async def get_subscription_plans(user_id: int):
    """Get available subscription plans (dummy implementation)."""
    return [
        {
            "plan_id": "free",
            "name": "Free Plan",
            "price": 0,
            "features": ["20 messages per day", "Basic models only", "5 messages context history"]
        },
        {
            "plan_id": "basic",
            "name": "Basic Plan",
            "price": 499,
            "features": ["100 messages per day", "Basic models only", "10 messages context history"]
        },
        {
            "plan_id": "pro",
            "name": "Pro Plan",
            "price": 999,
            "features": ["Unlimited messages", "All models", "20 messages context history"]
        }
    ]

@router.get("/subscriptions/active", response_model=SubscriptionResponse)
async def get_active_subscription(user_id: int):
    """Get the active subscription for the user (dummy implementation)."""
    # Always return a free subscription
    return {
        "subscription_id": 1,
        "user_id": user_id,
        "plan_name": "free",
        "start_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": None,
        "auto_renew": False
    }

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(user_id: int):
    """Get all subscriptions for the user (dummy implementation)."""
    # Just return a list with one free subscription
    return [{
        "subscription_id": 1,
        "user_id": user_id,
        "plan_name": "free",
        "start_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": None,
        "auto_renew": False
    }]

@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(subscription_data: SubscriptionCreate, user_id: int):
    """Create a new subscription for the user (dummy implementation)."""
    # Always return a subscription with the requested plan
    return {
        "subscription_id": 1,
        "user_id": user_id,
        "plan_name": subscription_data.plan_name,
        "start_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S") if subscription_data.plan_name != "free" else None,
        "auto_renew": subscription_data.auto_renew
    }

# --- Payment Routes ---

@router.post("/payments/order", response_model=OrderResponse)
async def create_payment_order(payment_data: PaymentCreate, user_id: int):
    """Create a payment order (dummy implementation)."""
    # Return a dummy order
    return {
        "order_id": f"order_{datetime.now().timestamp()}",
        "amount": 999 if payment_data.plan_id == "pro" else 499,
        "currency": payment_data.currency
    }

@router.post("/payments/verify", response_model=VerifyResponse)
async def verify_payment(verify_data: PaymentVerify, user_id: int):
    """Verify a payment and activate subscription (dummy implementation)."""
    # Return success response
    return {
        "success": True,
        "message": "Payment verified and subscription activated (dummy implementation)",
        "subscription": {
            "plan": "pro",
            "start_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "expiry_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        }
    } 
