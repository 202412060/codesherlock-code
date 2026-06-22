from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from datetime import datetime


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    balance: Optional[Decimal] = None
    is_active: Optional[bool] = None


class TransferRequest(BaseModel):
    recipient_id: int
    amount: Decimal
    note: Optional[str] = None


class TopUpRequest(BaseModel):
    amount: Decimal
    payment_method: str


class WalletResponse(BaseModel):
    user_id: int
    balance: Decimal
    currency: str = "USD"
    is_active: bool


class TransactionResponse(BaseModel):
    transaction_id: str
    sender_id: int
    recipient_id: int
    amount: Decimal
    status: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
