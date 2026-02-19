from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from BookStore.app.auth.auth import decode_access_token
from BookStore.app.models.user_model import User
from BookStore.app.database.user_db import USERS_DB
from BookStore.app.models.model import User as users
from BookStore.app.dependencies.db_dependencies import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/form")


def get_current_user_oauth2(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)) -> User:
    logger.info("Get current user oauth")
    payload = decode_access_token(token)
    if not payload:
        logger.debug("Not valid payload")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(users).filter(users.username == username).first()
    if not user or not user.is_active:
        logger.debug("User is invalid or not active")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return user

