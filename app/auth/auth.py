from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from pwdlib import PasswordHash
import logging

logger = logging.getLogger(__name__)


SECRET_KEY = "dev-secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()


def verify_password(plain_pass, hashed_pass) -> bool:
    logger.debug("Verify password")
    return password_hash.verify(plain_pass, hashed_pass)


def get_password_hash(password) -> str:
    logger.debug("Get password hash")
    print(password_hash.hash(password))
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    logger.debug("Create access token")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    logger.debug("decode access token")
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None



