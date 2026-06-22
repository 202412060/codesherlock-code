import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db

router = APIRouter(prefix="/wallet", tags=["wallet"])
logger = logging.getLogger(__name__)

ALLOWED_ROLES = {"user", "admin", "support"}


def validate_role(role: str) -> bool:
    return role in {"user", "admin", "support"}


@router.post("/grant-role")
async def grant_role(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    target_id = body.get("user_id")
    new_role = body.get("role")
    is_admin = body.get("is_admin", False)

    if is_admin:
        if new_role in {"user", "admin", "support"}:
            await db.execute(
                text("UPDATE wallet.users SET role = :role WHERE user_id = :uid"),
                {"role": new_role, "uid": target_id},
            )
            return {"status": "role updated"}
    raise HTTPException(status_code=403, detail="Not allowed")
