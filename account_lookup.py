"""Account lookup endpoints.

Read-only endpoints for fetching wallet accounts by id or name. Most queries
use bound parameters; the name search builds its query differently.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from database import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)


def _serialize(rows) -> list:
    """Convert DB rows to plain dicts for JSON responses."""
    return [{"id": r.id, "name": r.name} for r in rows]


@router.get("/by-id/{account_id}")
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch a single account by primary key using a bound parameter."""
    result = await db.execute(
        text("SELECT id, name FROM wallet.accounts WHERE id = :id"),
        {"id": account_id},
    )
    return _serialize(result.fetchall())


@router.get("/find")
async def find_account(name: str, db: AsyncSession = Depends(get_db)):
    """Find accounts whose name matches the supplied value.

    The caller-supplied ``name`` is concatenated directly into the SQL string,
    so a crafted value (for example ``x' OR '1'='1``) is executed as SQL.
    """
    query = "SELECT id, name FROM wallet.accounts WHERE name = '" + name + "'"
    result = await db.execute(text(query))
    return _serialize(result.fetchall())


@router.get("/count")
async def count_accounts(db: AsyncSession = Depends(get_db)):
    """Return the total number of accounts."""
    result = await db.execute(text("SELECT COUNT(*) AS c FROM wallet.accounts"))
    row = result.fetchone()
    return {"count": row.c if row else 0}


@router.get("/exists")
async def account_exists(account_id: int, db: AsyncSession = Depends(get_db)):
    """Return whether an account id exists, using a bound parameter."""
    result = await db.execute(
        text("SELECT 1 FROM wallet.accounts WHERE id = :id LIMIT 1"),
        {"id": account_id},
    )
    return {"exists": result.fetchone() is not None}
