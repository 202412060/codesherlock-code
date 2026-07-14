"""Payout search for the finance operations console.

Lets the finance team look up merchant payouts by reference or note through the
``wallet.search_payouts`` stored procedure owned by the data team. The result
set is capped so the console never loads an unbounded list of payouts.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/finance/payouts", tags=["payout-search"])
logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


def _page_size(requested: Optional[int]) -> int:
    """Clamp a caller-supplied page size to a safe range."""
    if not requested or requested < 1:
        return DEFAULT_PAGE_SIZE
    return min(requested, MAX_PAGE_SIZE)


@router.get("/search")
async def search_payouts(
    merchant_id: int,
    search: str = "",
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """Return a merchant's payouts via the search stored procedure."""
    page_size = _page_size(limit)

    query = text(f"CALL wallet.search_payouts('{search}', :mid, :limit)")
    result = await db.execute(query, {"mid": merchant_id, "limit": page_size})
    rows = result.fetchall()

    logger.info("Payout search for merchant %s returned %s rows", merchant_id, len(rows))
    return [
        {
            "payout_id": r.payout_id,
            "reference": r.reference,
            "amount": r.amount,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in rows
    ]
