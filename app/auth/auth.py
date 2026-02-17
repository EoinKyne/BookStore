from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from pwdlib import PasswordHash



SECRET_KEY = "dev-secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
password_hash = PasswordHash.recommended()


def verify_password(plain_pass, hashed_pass) -> bool:
    return password_hash.verify(plain_pass, hashed_pass)


def get_password_hash(password) -> str:
    print(password_hash.hash(password))
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None



