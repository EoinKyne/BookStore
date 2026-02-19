from sqlalchemy.orm import Session
from BookStore.app.models.model import User as UserModel
from BookStore.app.routes.users import User
from BookStore.app.auth.auth import get_password_hash
from BookStore.app.dependencies.db_dependencies import get_db
from sqlalchemy import select
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)


def init_admin(db: Session):
    logger.info("Init default user...")
    uname = "admin"
    stmt = select(UserModel).where(UserModel.username == uname)
    result = db.execute(stmt)

    if result:
        return

    packaged_user = UserModel(
        role="Administrator",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
    )
    db.add(packaged_user)
    db.commit()
    db.refresh(packaged_user)