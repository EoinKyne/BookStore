import logging

logger = logging.getLogger(__name__)


def test_create_user(api_request_authorized):
    logger.debug("Test create user...")
    response = api_request_authorized.post(
        "/users",
        data={
            "role": "Administrator",
            "username": "adminuserone",
            "hashed_password": "adminone123",
            "is_active": True,
        }
    )
    assert response.status == 200


def test_create_user_with_unavailable_username(api_request_authorized):
    logger.debug("Test create user with unavailable username ")
    response = api_request_authorized.post(
        "/users",
        data={
            "role": "Administrator",
            "username": "admin",
            "hashed_password": "admin1234",
            "is_active": True,
        }
    )
    assert response.status == 200
