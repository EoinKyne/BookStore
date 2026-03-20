import logging
import uuid

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from BookStore.app.auth.auth import get_password_hash, verify_password
from BookStore.app.models.model import Role as UserRole
from BookStore.app.models.model import User as UserModel
from BookStore.app.schemas.create_user import CreateUser
from BookStore.app.schemas.patch_user import UpdateIsActiveUser, UpdatePass
from BookStore.app.services import user_service

logger = logging.getLogger(__name__)


def test_get_user_returns_user(db_session):
    logger.debug("Test get user by id returns user")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests1",
        password=get_password_hash("test_pass_1"),
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
    logger.debug("Test get user by id not found raises 404")
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user_or_404(db_session, uuid.uuid4())
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_by_username(db_session):
    logger.debug("Test get username")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests2",
        password=get_password_hash("test_pass_1"),
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
    logger.debug("Test find username not found raises 404")
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_username_or_404(db_session, "someuserthatdoesnotexist")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_400_if_is_active_true(db_session):
    logger.debug("Test detail user if is_active is True")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests3",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests3").first()
    with pytest.raises(HTTPException) as exc_info:
        user_service.delete_user(db_session, user.id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_deactivate_user_if_is_active_false(db_session):
    logger.debug("Test deactivate is active from False to False ")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests4",
        password=get_password_hash("test_pass_1"),
        is_active=False,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests4").first()
    data = UpdateIsActiveUser(is_active=False)
    with pytest.raises(HTTPException) as exc_info:
        user_service.deactivate_user(db_session, user.id, data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_deactivate_user(db_session):
    logger.debug("Test deactivate is active from True to False ")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests5",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests5").first()
    data = UpdateIsActiveUser(is_active=False)

    result = user_service.deactivate_user(db_session, user.id, data)

    assert result == user
    assert result.is_active is False


def test_deactive_user_integrity_error(mocker):
    logger.debug("Test deactivate user integrity error")
    db = mocker.Mock()
    user = mocker.Mock()
    user.id = uuid.uuid4()
    user.is_active = True

    mocker.patch("BookStore.app.services.user_service.get_user_or_404", return_value=user)
    mocker.patch("BookStore.app.services.user_service.update_is_active_field", return_value=user)

    db.commit.side_effect = IntegrityError("stmt", "para", "orig")

    with pytest.raises(IntegrityError):
        user_service.deactivate_user(db, user_id=user.id, data=False)

    db.commit.assert_called_once()
    db.rollback.assert_called_once()


def test_activate_user_if_is_active_true(db_session):
    logger.debug("Test activate is active field from True to True")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests6",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests6").first()
    data = UpdateIsActiveUser(is_active=True)
    with pytest.raises(HTTPException) as exc_info:
        user_service.activate_user(db_session, user.id, data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_activate_user_if_is_active_false(db_session):
    logger.debug("Test activate is active field from false to true")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests7",
        password=get_password_hash("test_pass_1"),
        is_active=False,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests7").first()
    data = UpdateIsActiveUser(is_active=True)
    result = user_service.activate_user(db_session, user.id, data)

    assert result == user
    assert result.is_active is True


def test_activate_user_integrity_error(mocker):
    logger.debug("Test activate user integrity error")
    db = mocker.Mock()
    user = mocker.Mock()
    user.id = uuid.uuid4()
    user.is_active = False

    mocker.patch("BookStore.app.services.user_service.get_user_or_404", return_value=user)
    mocker.patch("BookStore.app.services.user_service.update_is_active_field", return_value=user)

    db.commit.side_effect = IntegrityError("stmt", "param", "orig")

    with pytest.raises(IntegrityError):
        user_service.activate_user(db, user_id=user.id, data=True)

    db.commit.assert_called_once()
    db.rollback.assert_called_once()


def test_update_is_active_field(db_session):
    logger.debug("Test update is active field")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests8",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests8").first()
    data = UpdateIsActiveUser(is_active=False)

    result = user_service.update_is_active_field(user, data)

    assert result == user
    assert result.is_active is False


def test_update_credentials(db_session):
    logger.debug("Test update credentials")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests9",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests9").first()
    data = UpdatePass(password="test_pass_12")

    result = user_service.update_credentials(db_session, user.id, data)

    assert result == user
    assert verify_password(data.password, result.password) is True


def test_delete_user(db_session):
    logger.debug("Test update is active field")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests10",
        password=get_password_hash("test_pass_1"),
        is_active=False,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests10").first()

    result = user_service.delete_user(db_session, user.id)

    assert result is None


def test_delete_user_integrity_error(mocker):
    logger.debug("Test delete user integrity error")
    db = mocker.Mock()
    user = mocker.Mock()
    user.id = uuid.uuid4()
    user.is_active = False

    mocker.patch("BookStore.app.services.user_service.get_user_or_404", return_value=user)

    db.commit.side_effect = IntegrityError("stmt", "param", "orig")

    with pytest.raises(IntegrityError):
        user_service.delete_user(db, user_id=user.id)

    db.delete.assert_called_once_with(user)
    db.commit.assert_called_once()
    db.rollback.assert_called_once()


def test_update_credentials_inactive_user(db_session):
    logger.debug("Test update credentials for user is active is false")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests10",
        password=get_password_hash("test_pass_1"),
        is_active=False,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests10").first()
    data = UpdatePass(password="test_pass_12")

    with pytest.raises(HTTPException) as exc_info:
        user_service.update_credentials(db_session, user.id, data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_update_credentials_user_integrity_error(mocker):
    logger.debug("Test delete user integrity error")
    db = mocker.Mock()
    user = mocker.Mock()
    user.id = uuid.uuid4()
    user.is_active = True

    mocker.patch("BookStore.app.services.user_service.get_user_or_404", return_value=user)
    credentials = UpdatePass(password="test_pass_12")

    db.commit.side_effect = IntegrityError("stmt", "param", "orig")

    with pytest.raises(IntegrityError):
        user_service.update_credentials(db, user_id=user.id, data=credentials)

    db.commit.assert_called_once()
    db.rollback.assert_called_once()


def test_check_roles_not_a_valid_role(db_session):
    logger.debug("Test check not a valid role")

    test_user = CreateUser(
        roles=["Notavalidrole"],
        username="adminunittests11",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    with pytest.raises(HTTPException) as exc_info:
        user_service.check_roles(db_session, test_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid Role"


def test_check_roles_valid_role(db_session):
    logger.debug("Test check not a valid role")

    test_user = CreateUser(
        roles=["Contributor"],
        username="adminunittests11",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    result = user_service.check_roles(db_session, test_user)

    assert result[0].name == "Contributor"
    assert isinstance(result, list)


def test_check_roles_valid_multiple_roles(db_session):
    logger.debug("Test check not a valid role")

    test_user = CreateUser(
        roles=["Administrator", "Contributor"],
        username="adminunittests11",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    result = user_service.check_roles(db_session, test_user)

    assert result[1].name == "Contributor"
    assert result[0].name == "Administrator"
    assert isinstance(result, list)


def test_create_user(db_session):
    logger.debug("Test create user")
    test_user = CreateUser(
        roles=["Contributor"],
        username="adminunittests12",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    result = user_service.create_user(db_session, test_user)

    user = db_session.query(UserModel).filter(UserModel.username == "adminunittests12").first()

    assert result.username == "adminunittests12"
    assert result.username == user.username
    assert result.roles[0].name == "Contributor"


def test_create_user_with_conflicting_username(db_session):
    logger.debug("Test create user with conflicting username")
    roles = (
        db_session.query(UserRole).filter(UserRole.name == "Contributor").first()
    )

    test_user = UserModel(
        roles=[roles],
        username="adminunittests13",
        password=get_password_hash("test_pass_1"),
        is_active=False,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    conflict_user = CreateUser(
        roles=["Contributor"],
        username="adminunittests13",
        password=get_password_hash("test_pass_1"),
        is_active=True,
    )

    with pytest.raises(HTTPException) as exc_info:
        user_service.create_user(db_session, conflict_user)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Username already exists"
