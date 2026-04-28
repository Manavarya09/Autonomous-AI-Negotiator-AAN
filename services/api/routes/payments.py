"""Stripe payment integration for subscriptions."""

import os
import stripe
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.api.routes.auth import get_current_user
from config.database.models import User

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

PLANS = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "jobs_per_month": 3,
        "features": ["Basic negotiation", "Dubizzle + OLX", "Email support"],
    },
    "pro": {
        "name": "Pro",
        "price_monthly": 9.99,
        "jobs_per_month": 50,
        "features": ["Advanced AI", "All platforms", "Priority support", "Auto-buy"],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 49.99,
        "jobs_per_month": -1,
        "features": ["Unlimited", "API access", "Team collaboration", "Custom integrations"],
    },
}


class StripeCheckoutSession(BaseModel):
    plan_id: str
    success_url: str
    cancel_url: str


class SubscriptionResponse(BaseModel):
    plan_id: str
    status: str
    current_period_end: Optional[str] = None


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: StripeCheckoutSession,
    current_user: User = Depends(get_current_user),
):
    """Create Stripe checkout session for subscription."""
    
    if request.plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = PLANS[request.plan_id]
    
    if plan["price_monthly"] == 0:
        raise HTTPException(status_code=400, detail="Free plan doesn't need payment")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "aed",
                        "product_data": {
                            "name": f"AAN {plan['name']} Plan",
                            "description": f"{plan['jobs_per_month']} jobs per month",
                        },
                        "unit_amount": int(plan["price_monthly"] * 100),
                        "recurring": {"interval": "month"},
                    },
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={"user_id": str(current_user.id), "plan_id": request.plan_id},
        )
        
        return {"session_id": session.id, "url": session.url}
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(payload: bytes, signature: str):
    """Handle Stripe webhooks."""
    
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        plan_id = session["metadata"]["plan_id"]
        
        # Update user subscription in database
        # await update_user_subscription(user_id, plan_id)
        print(f"User {user_id} subscribed to {plan_id}")
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        # Handle cancellation
        print(f"Subscription {subscription['id']} cancelled")
    
    return {"received": True}


@router.get("/plans")
async def get_plans():
    """Get available subscription plans."""
    return {
        plan_id: {**details, "price_display": f"AED {details['price_monthly']}/month"}
        for plan_id, details in PLANS.items()
    }


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
):
    """Get current user's subscription."""
    # In production, fetch from user's subscription field
    return {
        "plan_id": "free",
        "status": "active",
        "jobs_used": 0,
        "jobs_limit": PLANS["free"]["jobs_per_month"],
    }


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
):
    """Cancel user's subscription."""
    
    # In production, find and cancel Stripe subscription
    return {"status": "cancelled", "message": "Subscription cancelled"}


@router.post("/create-portal-session")
async def create_portal_session(
    current_user: User = Depends(get_current_user),
):
    """Create Stripe customer portal session."""
    
    # In production, create portal link for billing management
    return {"url": "/settings/billing"}