import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from BookStore.app.auth.auth import get_password_hash
from BookStore.app.models.model import Role as UserRole
from BookStore.app.models.model import User as UserModel

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