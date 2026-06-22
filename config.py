import os

APP_ENV = os.getenv("APP_ENV", "local")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://wallet_user:wallet_pass@localhost:5432/walletdb",
)
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_PORT = int(os.getenv("DB_PORT"))

SECRET_KEY = os.getenv("SECRET_KEY", "wallet-super-secret-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRY", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_EXPIRY", "7"))

PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "https://api.payments.internal/v1")
PAYMENT_GATEWAY_KEY = os.getenv("PAYMENT_GATEWAY_KEY")
PAYMENT_GATEWAY_TIMEOUT = int(os.getenv("PAYMENT_GATEWAY_TIMEOUT", "30"))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "wallet_transactions")

MAX_TRANSFER_AMOUNT = float(os.getenv("MAX_TRANSFER_AMOUNT", "10000.0"))
MIN_TRANSFER_AMOUNT = 0.01
DAILY_TRANSFER_LIMIT = float(os.getenv("DAILY_TRANSFER_LIMIT", "50000.0"))

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
