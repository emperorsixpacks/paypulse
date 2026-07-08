import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from src.paypulse.core.settings import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_api_key(is_live: bool = False) -> tuple[str, str]:
    prefix = "pp_live" if is_live else "pp_test"
    full_key = f"{prefix}_{secrets.token_urlsafe(32)}"
    hashed = bcrypt.hashpw(full_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return full_key, hashed
