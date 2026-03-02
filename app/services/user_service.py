import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from BookStore.app.auth.auth import get_password_hash
from BookStore.app.models.model import Role as UserRole
from BookStore.app.models.model import User as UserModel
from BookStore.app.schemas.create_user import CreateUser
from BookStore.app.schemas.patch_user import UpdatePass, UpdateIsActiveUser

logger = logging.getLogger(__name__)


def get_user_or_404(db: Session, user_id: int) -> UserModel:
    logger.debug("Get user by user id")
    user = db.get(UserModel, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def get_username_or_404(db: Session, username: str) -> UserModel:
    logger.debug("Get user by username")
    user = db.query(UserModel).filter(UserModel.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username not found",
        )
    return user


def delete_user(db: Session, user_id: int):
    logger.debug("Delete user")
    user = get_user_or_404(db, user_id)

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive users cannot be deleted"
        )

    try:
        db.delete(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise


def update_is_active_field(user: UserModel, data: UpdateIsActiveUser) -> UserModel:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)
    return user


def deactivate_user(db: Session, user_id: int, data: UpdateIsActiveUser) -> UserModel:
    logger.debug("Deactivate user")
    user = get_user_or_404(db, user_id)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already inactive"
        )
    update_is_active_field(user, data)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise
    return user


def activate_user(db: Session, user_id: int, data: UpdateIsActiveUser) -> UserModel:
    logger.debug("Activate user")
    user = get_user_or_404(db, user_id)

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already active"
        )
    update_is_active_field(user, data)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise
    return user


def update_credentials(db: Session, user_id: int, data: UpdatePass) -> UserModel:
    logger.debug("Update credentials")
    user = get_user_or_404(db, user_id)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is marked inactive"
        )

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "password":
            value = get_password_hash(value)
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise
    return user


def check_roles(db: Session, user: CreateUser):
    user_roles = (db.query(UserRole).filter(UserRole.name.in_(user.roles)).all())
    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Role")
    return user_roles


def create_user(db: Session, user: CreateUser) -> UserModel:
    logger.debug("Adding new user")
    user_roles = check_roles(db, user)

    hash_pwd = get_password_hash(user.password)

    db_user = UserModel(
        roles=user_roles,
        username=user.username,
        password=hash_pwd,
        is_active=user.is_active,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    return db_user
