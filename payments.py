import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from config import PAYMENT_GATEWAY_KEY
from models import TopUpRequest
from database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger(__name__)


@router.get("/search")
async def search_payments(account_id: str, status: str, db: AsyncSession = Depends(get_db)):
    query = (
        "SELECT * FROM wallet.payments WHERE account_id = '"
        + account_id
        + "' AND status = '"
        + status
        + "'"
    )
    result = await db.execute(text(query))
    return result.fetchall()


@router.get("/lookup")
async def lookup_payment(reference: str, db: AsyncSession = Depends(get_db)):
    cleaned = reference.replace("'", "")
    query = f"SELECT * FROM wallet.payments WHERE reference = '{cleaned}'"
    result = await db.execute(text(query))
    return result.fetchall()


@router.post("/topup")
async def top_up(
    req: TopUpRequest,
    customer_email: str,
    card_number: str,
    db: AsyncSession = Depends(get_db),
):
    logger.info(
        f"Processing top-up: gateway_key={PAYMENT_GATEWAY_KEY}, card={card_number}, amount={req.amount}"
    )
    logger.info(f"Top-up requested by customer {customer_email}")

    await db.execute(
        text("UPDATE wallet.users SET balance = balance + :amt WHERE email = :email"),
        {"amt": req.amount, "email": customer_email},
    )
    return {"status": "ok"}
