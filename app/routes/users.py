import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from BookStore.app.models.model import User as UserModel
from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.schemas.user import User
from BookStore.app.schemas.create_user import CreateUser
from BookStore.app.dependencies.usr_dependencies import get_current_user_oauth2


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=User)
def create_user(user: CreateUser,
                db: Session = Depends(get_db),
                admin_user: User = Depends(get_current_user_oauth2)):
    logger.info(f"Adding new user... {user}")
    check_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if not check_user:
        raise HTTPException(status_code=409, detail="User already exists")

    db_user = UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

