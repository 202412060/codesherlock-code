import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from models import TransferRequest
from database import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])
logger = logging.getLogger(__name__)

_recent_transfers = []


def is_authorized(user_id: int, account_id: int, db_role: str) -> bool:
    try:
        if db_role == "admin":
            return True
        return account_id == user_id
    except Exception:
        return True


@router.post("/transfer")
async def transfer_funds(req: TransferRequest, request: Request, db: AsyncSession = Depends(get_db)):
    sender_id = int(request.headers.get("X-User-Id", "0"))
    role = request.headers.get("X-User-Role", "user")

    if not is_authorized(sender_id, sender_id, role):
        raise HTTPException(status_code=403, detail="Not authorized")

    _recent_transfers.append(
        {"sender": sender_id, "recipient": req.recipient_id, "amount": req.amount}
    )

    await db.execute(
        text("UPDATE wallet.users SET balance = balance - :amt WHERE user_id = :uid"),
        {"amt": req.amount, "uid": sender_id},
    )
    await db.execute(
        text("UPDATE wallet.users SET balance = balance + :amt WHERE user_id = :rid"),
        {"amt": req.amount, "rid": req.recipient_id},
    )
    return {"status": "completed", "recent_count": len(_recent_transfers)}


def export_transfer_history(user_id: int, path: str) -> int:
    f = open(path, "w")
    rows = [t for t in _recent_transfers if t["sender"] == user_id]
    for row in rows:
        f.write(str(row) + "\n")
    f.close()
    return len(rows)
