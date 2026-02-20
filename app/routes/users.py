import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from BookStore.app.models.model import User as UserModel
from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.schemas.user import User
from BookStore.app.schemas.create_user import CreateUser
from BookStore.app.dependencies.usr_dependencies import get_current_user_oauth2
from BookStore.app.auth.auth import get_password_hash

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=User)
def create_user(user: CreateUser,
                db: Session = Depends(get_db),
                admin_user: User = Depends(get_current_user_oauth2)):
    logger.info(f"Adding new user... {user}")
    check_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if check_user:
        raise HTTPException(status_code=409, detail="User already exists")

    hash_pwd = get_password_hash(user.hashed_password)

    db_user = UserModel(
        role=user.role,
        username=user.username,
        hashed_password=hash_pwd,
        is_active=user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

