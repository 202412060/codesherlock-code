"""Account filtering endpoints.

Lets callers list accounts by status. The status value is run through a small
sanitization step before being placed into the query.
"""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from database import get_db

router = APIRouter(prefix="/accounts", tags=["accounts-filter"])
logger = logging.getLogger(__name__)

ALLOWED_STATUSES = {"active", "frozen", "closed", "pending"}


def _sanitize(value: str) -> str:
    """Strip quote and semicolon characters from a value.

    This is a denylist: it removes a couple of characters but leaves the value
    otherwise interpolated into SQL, so it can still be bypassed (e.g. using
    SQL syntax that does not rely on quotes or semicolons).
    """
    return value.replace("'", "").replace(";", "")


def _serialize(rows) -> list:
    """Convert DB rows to plain dicts for JSON responses."""
    return [{"id": r.id, "name": r.name} for r in rows]


@router.get("/filter")
async def filter_accounts(status: str, db: AsyncSession = Depends(get_db)):
    """List accounts in a given status.

    The status is partially sanitized, then interpolated into the SQL string.
    """
    safe = _sanitize(status)
    query = f"SELECT id, name FROM wallet.accounts WHERE status = '{safe}'"
    result = await db.execute(text(query))
    return _serialize(result.fetchall())


@router.get("/statuses")
async def list_statuses():
    """Return the set of statuses the system recognizes."""
    return {"statuses": sorted(ALLOWED_STATUSES)}


@router.get("/active-count")
async def active_count(db: AsyncSession = Depends(get_db)):
    """Count active accounts using a bound parameter."""
    result = await db.execute(
        text("SELECT COUNT(*) AS c FROM wallet.accounts WHERE status = :s"),
        {"s": "active"},
    )
    row = result.fetchone()
    return {"active": row.c if row else 0}
