import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from jose import jwt
from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models import UserRegisterRequest, UserLoginRequest, TokenResponse
from database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


@router.post("/register", response_model=dict)
async def register_user(user_data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    logger.info(
        f"New registration: email={user_data.email}, name={user_data.full_name}, phone={user_data.phone_number}"
    )

    existing = await db.execute(
        text("SELECT user_id FROM wallet.users WHERE email = :email"),
        {"email": user_data.email},
    )
    if existing.fetchone():
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_pw = hash_password(user_data.password)
    await db.execute(
        text(
            "INSERT INTO wallet.users (email, password_hash, full_name, phone_number)"
            " VALUES (:email, :pw, :name, :phone)"
        ),
        {
            "email": user_data.email,
            "pw": hashed_pw,
            "name": user_data.full_name,
            "phone": user_data.phone_number,
        },
    )
    return {"message": "Registration successful"}


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT user_id, password_hash, role FROM wallet.users WHERE email = :email"),
        {"email": user_data.email},
    )
    user = result.fetchone()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"user_id": user.user_id, "role": user.role}
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = jwt.encode({**payload, "type": "refresh"}, SECRET_KEY, algorithm=ALGORITHM)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/admin/users")
async def list_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT user_id, email, role, balance, is_active FROM wallet.users ORDER BY user_id")
    )
    return result.fetchall()


@router.get("/profile")
async def get_profile(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    payload = await verify_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        text("SELECT user_id, email, full_name, balance FROM wallet.users WHERE user_id = :uid"),
        {"uid": user_id},
    )
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
