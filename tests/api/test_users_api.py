import logging
from playwright.sync_api import APIRequestContext

logger = logging.getLogger(__name__)


def test_create_user(api_request_authorized):
    logger.debug("Test create user...")
    response = api_request_authorized.post(
        "/users",
        data={
            "role": "Contributor",
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
            "role": "Contributor",
            "username": "admin",
            "hashed_password": "admin1234",
            "is_active": True,
        }
    )
    assert response.status == 409


def test_get_users(api_request_authorized):
    logger.debug("Test get all users...")
    create_response = api_request_authorized.post(
        "/users",
        data={
            "role": "Contributor",
            "username": "newadministrator",
            "hashed_password": "bkstore123",
            "is_active": "True"
        }
    )
    response = api_request_authorized.get("/users")
    assert response.status == 200
    assert isinstance(response.json(), list)


def test_get_user_by_id(api_request_authorized):
    logger.debug("Test get user by id")
    create_response = api_request_authorized.post(
        "users",
        data={
            "role": "Contributor",
            "username": "newadministrator1",
            "hashed_password": "bkstore123",
            "is_active": "True"
        }
    )

    user_id = create_response.json()["id"]

    response = api_request_authorized.get(f"/users/user_id/{user_id}")
    assert response.status == 200
    body = response.json()
    assert body["id"] == user_id
    assert body["role"] == "Contributor"
    assert body["username"] == "newadministrator1"
    assert body["is_active"] is True


def test_get_user_by_username(api_request_authorized):
    logger.debug("Test get user by username")
    create_response = api_request_authorized.post(
        "/users",
        data={
          "role": "Contributor",
          "username": "newusertoget",
          "hashed_password": "bkstore123",
          "is_active": "True"
        })

    usrname = create_response.json()["username"]

    response = api_request_authorized.get(f"/users/username/{usrname}")
    assert response.status == 200
    body = response.json()
    assert body["username"] == "newusertoget"
    assert body["role"] == "Contributor"
    assert body["is_active"] is True


def test_update_is_active_for_user(api_request_authorized):
    logger.debug("Test update is active for user")
    create_response = api_request_authorized.post(
        "/users",
        data={
            "role": "Contributor",
            "username": "newadministrator2",
            "hashed_password": "bkstore123",
            "is_active": "True"
        }
    )
    user_id = create_response.json()["id"]

    response = api_request_authorized.patch(
        f"/users/is_active/{user_id}",
        data={
            "is_active": "False"
        }
    )
    assert response.status == 200
    body = response.json()
    assert body["is_active"] is False
    assert body["is_active"] is not True


def test_update_pass_for_user(api_request_authorized):
    logger.debug("Test update pass for user")

    usrname = "admin"

    create_response = api_request_authorized.get(
        f"/users/username/{usrname}"
    )
    user_id = create_response.json()["id"]

    response = api_request_authorized.patch(
        f"/users/credentials/{user_id}",
        data={
            "hashed_password": "admin1234"
        }
    )

    assert response.status == 200
    body = response.json()
    user_id = create_response.json()["id"]
    api_request_authorized.patch(f"/users/credentials/{user_id}",
                                 data={
                                     "hashed_password": "admin123"
                                 })


def test_delete_user(api_request_authorized):
    logger.debug("Test delete user")
    create_response = api_request_authorized.post(
        "/users",
        data={
            "role": "Contributor",
            "username": "newadministrator4",
            "hashed_password": "bkstore123",
            "is_active": "False"
        }
    )

    user_id = create_response.json()["id"]
    response = api_request_authorized.delete(
        f"/users/{user_id}"
    )
    assert response.status == 204
