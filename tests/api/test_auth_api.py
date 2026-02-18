import logging


logger = logging.getLogger(__name__)


def test_login_form(api_request_not_authorized):
    logger.debug("Test login form")

    login = api_request_not_authorized.post(
        "/auth/login/form",
        form={
            "username": "admin",
            "password": "admin123",
        }
    )
    assert login.status == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"] is not None


def test_login_form_with_invalid_user(api_request_not_authorized):
    logger.debug("Test login with invalid user")

    login = api_request_not_authorized.post(
        "/auth/login/form",
        form={
            "username": "notadmin",
            "password": "admin123",
        }
    )
    assert login.status == 401
    assert login.json()["detail"] == "Invalid User"

