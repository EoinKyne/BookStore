import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.dependencies.usr_dependencies import requre_permission
from BookStore.app.models.model import User as UserModel
from BookStore.app.schemas.create_user import CreateUser
from BookStore.app.schemas.patch_user import UpdateIsActiveUser, UpdatePass
from BookStore.app.schemas.user import User
from BookStore.app.schemas.user_response_schema import UserResponse
from BookStore.app.services import user_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=UserResponse)
def create_user(user: CreateUser,
                db: Session = Depends(get_db),
                admin_user: User = Depends(requre_permission("admin:full"))):
    logger.info(f"Adding new user...")
    db_user = user_service.create_user(db, user)

    return db_user


@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db),
              limit: int = Query(10, ge=1, le=100),
              offset: int = Query(0, ge=0),
              admin_user: User = Depends(requre_permission("admin:full"))):
    logger.info("Get users...")

    users = (db.query(UserModel).order_by(UserModel.id.desc()))

    return users.offset(offset).limit(limit).all()


@router.get("/user_id/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int,
                   db: Session = Depends(get_db),
                   admin_user: User = Depends(requre_permission("admin:full"))):
    logger.info("Get user by id")
    user = user_service.get_user_or_404(db, user_id)

    return user


@router.get("/username/{username}", response_model=UserResponse)
def get_user_by_username(username: str,
                         db: Session = Depends(get_db),
                         admin_user: User = Depends(requre_permission("admin:full"))):
    logger.info("Get user by username")

    user = user_service.get_username_or_404(db, username)

    return user


@router.patch("/deactivate/{user_id}", response_model=UserResponse)
def deactivate_user(user_id: int,
                    data: UpdateIsActiveUser,
                    db: Session = Depends(get_db),
                    admin_user: User = Depends(requre_permission("admin:full"))):
    logger.info("Update is active for user")
    user = user_service.deactivate_user(db, user_id, data)

    return user


@router.patch("/activate/{user_id}", response_model=UserResponse)
def activate_user(user_id: int,
                  data: UpdateIsActiveUser,
                  db: Session = Depends(get_db),
                  admin_user: User = Depends(requre_permission("admin:full"))):
    logger.debug("Update is active for user")
    user = user_service.activate_user(db, user_id, data)

    return user


@router.patch("/credentials/{user_id}", response_model=UserResponse)
def update_creds(user_id: int,
                  data: UpdatePass,
                  db: Session = Depends(get_db),
                  admin_user: User = Depends(requre_permission("admin:full"))):
    logger.info("Update credentials for user")

    user = user_service.update_credentials(db, user_id, data)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int,
                db: Session = Depends(get_db),
                admin_user: User = Depends(requre_permission("admin:full"))):
    logger.info("Delete user")

    user_service.delete_user(db, user_id)
