import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from BookStore.app.services import user_service
from BookStore.app.models.model import User as UserModel
from BookStore.app.models.model import Role as UserRole
from BookStore.app.schemas.patch_user import UpdateIsActiveUser
from BookStore.app.auth.auth import get_password_hash
import logging

logger = logging.getLogger(__name__)


def test_get_user_returns_user(db_session):
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests1",
        password=get_password_hash("admin123"),
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests1").first()

    result = user_service.get_user_or_404(db_session, user.id)

    assert result == user
    assert result.id == user.id


def test_get_user_raises_404(db_session):

    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user_or_404(db_session, 99999)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_by_username(db_session):
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests2",
        password=get_password_hash("admin123"),
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests2").first()

    result = user_service.get_username_or_404(db_session, user.username)

    assert result == user
    assert result.username == user.username


def test_get_user_by_username_raises_404(db_session):

    with pytest.raises(HTTPException) as exc_info:
        user_service.get_username_or_404(db_session, "someuserthatdoesnotexist")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_400_if_is_active_true(db_session):
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests3",
        password=get_password_hash("admin123"),
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests3").first()
    with pytest.raises(HTTPException) as exc_info:
        user_service.delete_user(db_session, user.id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST




