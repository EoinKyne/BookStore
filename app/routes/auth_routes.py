from fastapi import APIRouter, Depends, HTTPException, status
from BookStore.app.auth.auth import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from BookStore.app.schemas.auth import TokenResponse
from BookStore.app.auth.auth import verify_password
from BookStore.app.database.user_db import USERS_DB
from BookStore.app.dependencies.db_dependencies import get_db
from sqlalchemy.orm import Session
from BookStore.app.models.model import User as users
from BookStore.app.auth.auth import decode_access_token
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login/form", response_model=TokenResponse)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login user: {form_data.username}")
    user = db.query(users).filter(users.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.debug("Failed login form")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


