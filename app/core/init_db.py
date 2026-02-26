from sqlalchemy.orm import Session
from BookStore.app.models.model import User as UserModel
from BookStore.app.models.model import Role as UserRole
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
    result = db.execute(stmt).scalars().unique().one_or_none()

    if result:
        return

    packaged_user = UserModel(
        roles=[db.query(UserRole).filter(UserRole.name == "Administrator").first()],
        username="admin",
        password=get_password_hash("admin123"),
        is_active=True,
    )
    db.add(packaged_user)
    db.commit()
    db.refresh(packaged_user)