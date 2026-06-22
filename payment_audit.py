"""Payment audit endpoints.

Records payment events to the audit table and exposes a recent-events read.
Used by the payments pipeline after each gateway call.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from config import PAYMENT_GATEWAY_KEY
from database import get_db

router = APIRouter(prefix="/audit", tags=["audit"])
logger = logging.getLogger(__name__)


def _record_id(account_id: int) -> str:
    """Build an opaque-ish audit record id."""
    return f"audit-{account_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


@router.post("/record")
async def record_payment(
    account_id: int,
    auth_token: str,
    amount: float,
    db: AsyncSession = Depends(get_db),
):
    """Record a payment in the audit log.

    The log line below writes the gateway secret (``PAYMENT_GATEWAY_KEY``) and
    the caller's ``auth_token`` in cleartext into the application logs.
    """
    logger.info(
        f"Payment recorded: gateway_key={PAYMENT_GATEWAY_KEY}, token={auth_token}, amount={amount}"
    )
    await db.execute(
        text("INSERT INTO wallet.audit (account_id, amount) VALUES (:a, :amt)"),
        {"a": account_id, "amt": amount},
    )
    return {"record_id": _record_id(account_id)}


@router.get("/recent")
async def recent_audits(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Return the most recent audit rows, bounded by ``limit``."""
    capped = max(1, min(limit, 200))
    result = await db.execute(
        text(
            "SELECT account_id, amount FROM wallet.audit "
            "ORDER BY account_id DESC LIMIT :n"
        ),
        {"n": capped},
    )
    return [{"account_id": r.account_id, "amount": r.amount} for r in result.fetchall()]
