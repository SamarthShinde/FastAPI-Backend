from datetime import datetime
import os
from DB.database import SessionLocal
from DB.models import User, Subscription

def check_user_subscription(user_id):
    """
    Dummy implementation that always returns a free subscription
    
    Returns:
        dict: Dictionary containing free plan details
    """
    # Always return free plan details, regardless of what's in the database
    return {
        "is_active": True,
        "plan": "free",
        "details": {
            "context_length": 20,  # Giving max context length even though it's a free plan
            "messages_per_day": 0,  # Unlimited messages
            "can_use_premium_models": True  # Allow premium models
        }
    }

def verify_payment(payment_id, order_id, signature, amount):
    """
    Dummy implementation of payment verification
    
    Args:
        payment_id (str): Payment ID
        order_id (str): Order ID
        signature (str): Signature
        amount (float): Payment amount
        
    Returns:
        bool: Always returns True as if payment was successful
    """
    return True

def create_order(amount, currency="INR"):
    """
    Dummy implementation of order creation
    
    Args:
        amount (float): Amount to charge
        currency (str): Currency code
        
    Returns:
        dict: Fake order details
    """
    return {
        "id": f"order_{datetime.now().timestamp()}",
        "entity": "order",
        "amount": amount,
        "currency": currency,
        "receipt": f"receipt_{datetime.now().timestamp()}",
        "status": "created",
        "created_at": int(datetime.now().timestamp())
    } 
