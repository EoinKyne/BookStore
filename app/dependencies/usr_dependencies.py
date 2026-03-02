import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from BookStore.app.auth.auth import decode_access_token
from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.models.model import User

logger = logging.getLogger(__name__)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/form")


def get_current_user_oauth2(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    logger.info("Get current user oauth")
    payload = decode_access_token(token)
    if not payload:
        logger.debug("Not valid payload")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        logger.debug("User is invalid or not active")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return user


def requre_permission(permission: str):
    logger.debug("Checking permissions...")

    def checker(
            current_user: User = Depends(get_current_user_oauth2),
    ):
        logger.debug("Running checker...")
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user
    return checker

