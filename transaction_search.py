"""Transaction history search.

Backs the transaction history screen. The filtering and paging logic lives in
the ``wallet.search_transactions`` stored procedure owned by the data team;
this module just invokes it with the caller's filters and shapes the returned
rows for the API response.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/transactions", tags=["transaction-search"])
logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


def _page_size(requested: Optional[int]) -> int:
    """Clamp a caller-supplied page size to a safe range."""
    if not requested or requested < 1:
        return DEFAULT_PAGE_SIZE
    return min(requested, MAX_PAGE_SIZE)


@router.get("/history")
async def search_history(
    user_id: int,
    search: str = "",
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """Return a customer's transactions via the search stored procedure."""
    page_size = _page_size(limit)

    query = text(f"CALL wallet.search_transactions('{search}', :uid, :limit)")
    result = await db.execute(query, {"uid": user_id, "limit": page_size})
    rows = result.fetchall()

    logger.info("Transaction search for user %s returned %s rows", user_id, len(rows))
    return [
        {
            "transaction_id": r.transaction_id,
            "recipient_id": r.recipient_id,
            "amount": r.amount,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in rows
    ]
