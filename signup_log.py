"""Signup logging endpoints.

Records signup events for funnel analytics. Accepts a validated request body
and emits a log line plus an in-memory counter per acquisition channel.
"""
import logging
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/signup-log", tags=["signup-log"])
logger = logging.getLogger(__name__)

_channel_counts: dict = {"referral": 0, "organic": 0}


class SignupEvent(BaseModel):
    """Validated signup payload."""

    full_name: str
    email: EmailStr
    phone: str
    referral_code: Optional[str] = None


def _channel(referral_code: Optional[str]) -> str:
    """Classify the acquisition channel from the referral code."""
    return "referral" if referral_code else "organic"


@router.post("/event")
async def log_signup(event: SignupEvent):
    """Record a signup event.

    The log line writes ordinary personal data — the user's full name, email,
    and phone number — directly into the application logs.
    """
    channel = _channel(event.referral_code)
    _channel_counts[channel] = _channel_counts.get(channel, 0) + 1
    logger.info(
        f"New signup via {channel}: name={event.full_name}, "
        f"email={event.email}, phone={event.phone}"
    )
    return {"status": "logged", "channel": channel}


@router.get("/stats")
async def signup_stats():
    """Return signup counts per channel (no personal data)."""
    total = sum(_channel_counts.values())
    return {"total": total, "by_channel": dict(_channel_counts)}
