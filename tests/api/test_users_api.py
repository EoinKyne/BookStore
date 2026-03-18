import logging

logger = logging.getLogger(__name__)


def test_create_user(api_request_admin):
    logger.debug("Test create user...")
    response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor1",
            "password": "contribone123",
            "is_active": True,
        }
    )
    assert response.status == 200


def test_create_user_unauthorized(api_request_not_authorized):
    logger.debug("Test create user unauthorized")
    response = api_request_not_authorized.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor2",
            "password": "contrib123",
            "is_active": True,
        }
    )
    assert response.status == 401
    assert response.status != 200


def test_create_user_with_unavailable_username(api_request_admin):
    logger.debug("Test create user with unavailable username ")
    response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "admin",
            "password": "admin1234",
            "is_active": True,
        }
    )
    assert response.status == 409


def test_get_users(api_request_admin):
    logger.debug("Test get all users...")
    create_response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor3",
            "password": "bkstore123",
            "is_active": "True"
        }
    )
    response = api_request_admin.get("/users")
    assert response.status == 200
    assert isinstance(response.json(), list)


def test_get_users_invalid_permissions(api_request_contributor):
    logger.info("Test get all users with invalid permissions")
    response = api_request_contributor.get("/users")
    logger.info(response.json())
    assert response.status == 403


def test_get_users_unauthorized(api_request_admin, api_request_not_authorized):
    logger.debug("Test get all users unauthorized")
    create_response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor4",
            "password": "bkstore123",
            "is_active": "True"
        }
    )
    response = api_request_not_authorized.get("/users")
    assert response.status == 401
    assert response.status != 200


def test_get_user_by_id(api_request_admin):
    logger.debug("Test get user by id")
    create_response = api_request_admin.post(
        "users",
        data={
            "roles": ["Contributor"],
            "username": "contributor5",
            "password": "bkstore123",
            "is_active": "True"
        }
    )

    user_id = create_response.json()["id"]

    response = api_request_admin.get(f"/users/user_id/{user_id}")
    assert response.status == 200
    body = response.json()
    assert body["roles"][0]["name"] == "Contributor"
    assert body["username"] == "contributor5"
    assert body["is_active"] is True


def test_get_user_by_id_unauthorized(api_request_admin, api_request_not_authorized):
    logger.debug("Test get user by id unauthorized")
    create_response = api_request_admin.post(
        "users",
        data={
            "roles": ["Contributor"],
            "username": "contributor6",
            "password": "bkstore123",
            "is_active": "True"
        }
    )

    user_id = create_response.json()["id"]

    response = api_request_not_authorized.get(f"/users/user_id/{user_id}")
    assert response.status == 401
    assert response.status != 200


def test_get_user_by_username(api_request_admin):
    logger.debug("Test get user by username")
    create_response = api_request_admin.post(
        "/users",
        data={
          "roles": ["Contributor"],
          "username": "contributor7",
          "password": "bkstore123",
          "is_active": "True"
        })

    usrname = create_response.json()["username"]

    response = api_request_admin.get(f"/users/username/{usrname}")
    assert response.status == 200
    body = response.json()
    assert body["username"] == "contributor7"
    assert body["roles"][0]["name"] == "Contributor"
    assert body["is_active"] is True


def test_get_user_by_username_unauthorized(api_request_admin, api_request_not_authorized):
    logger.debug("Test get user by username unauthorized")
    create_response = api_request_admin.post(
        "/users",
        data={
          "roles": ["Contributor"],
          "username": "contributor8",
          "password": "bkstore123",
          "is_active": "True"
        })

    usrname = create_response.json()["username"]

    response = api_request_not_authorized.get(f"/users/username/{usrname}")
    assert response.status == 401
    assert response.status != 200


def test_update_deactivate_is_active_for_user(api_request_admin):
    logger.debug("Test update is active for user")
    create_response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor9",
            "password": "bkstore123",
            "is_active": "True"
        }
    )
    user_id = create_response.json()["id"]

    response = api_request_admin.patch(
        f"/users/deactivate/{user_id}",
        data={
            "is_active": "False"
        }
    )
    assert response.status == 200
    body = response.json()
    assert body["is_active"] is False
    assert body["is_active"] is not True


def test_update_is_active_for_user_unauthorized(api_request_admin, api_request_not_authorized):
    logger.debug("Test update is active for user by unauthorized")
    create_response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor10",
            "password": "bkstore123",
            "is_active": "True"
        }
    )
    user_id = create_response.json()["id"]

    response = api_request_not_authorized.patch(
        f"/users/deactivate/{user_id}",
        data={
            "is_active": "False"
        }
    )
    assert response.status == 401
    assert response.status != 200


def test_update_pass_for_user(api_request_admin):
    logger.debug("Test update pass for user")

    usrname = "admin"

    create_response = api_request_admin.get(
        f"/users/username/{usrname}"
    )
    user_id = create_response.json()["id"]

    response = api_request_admin.patch(
        f"/users/credentials/{user_id}",
        data={
            "password": "admin1234"
        }
    )

    assert response.status == 200
    user_id = create_response.json()["id"]
    api_request_admin.patch(f"/users/credentials/{user_id}",
                            data={
                                     "password": "admin123"
                                 })


def test_update_pass_for_user_unauthorized(api_request_admin, api_request_not_authorized):
    logger.debug("Test update pass for user by unauthorized")
    usrname = "admin"
    create_response = api_request_admin.get(
        f"/users/username/{usrname}"
    )
    user_id = create_response.json()["id"]

    response = api_request_not_authorized.patch(
        f"/users/credentials/{user_id}",
        data={
            "password": "admin1234"
        }
    )

    assert response.status == 401
    assert response.status != 200


def test_delete_user(api_request_admin):
    logger.debug("Test delete user")
    create_response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor11",
            "password": "bkstore123",
            "is_active": "False"
        }
    )

    user_id = create_response.json()["id"]
    response = api_request_admin.delete(
        f"/users/{user_id}"
    )
    assert response.status == 204


def test_delete_user_unauthorized(api_request_admin, api_request_not_authorized):
    logger.debug("Test delete with unauthorized")
    create_response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor12",
            "password": "bkstore123",
            "is_active": "False"
        }
    )
    user_id = create_response.json()["id"]
    response = api_request_not_authorized.delete(
        f"/users/{user_id}"
    )
    assert response.status == 401
    assert response.status != 204


def test_update_activate_is_active_to_true_admin(api_request_admin):
    logger.debug("Update is active to true for user")
    create_response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor13",
            "password": "bkstore123",
            "is_active": "False"
        }
    )
    user_id = create_response.json()["id"]

    response = api_request_admin.patch(
        f"/users/activate/{user_id}",
        data={
            "is_active": True
        }
    )

    assert response.status == 200
    body = response.json()
    assert body["is_active"] is True
    assert body["is_active"] is not False


def test_update_is_active_to_true_unauthorized(api_request_admin, api_request_not_authorized):
    logger.debug("Test set is active to true for unauthorized user")
    create_response = api_request_admin.post(
        "/users",
        data={
            "roles": ["Contributor"],
            "username": "contributor14",
            "password": "bkstore123",
            "is_active": "False"
        }
    )
    user_id = create_response.json()["id"]

    response = api_request_not_authorized.patch(
        f"/users/activate/{user_id}",
        data={
            "is_active": "True"
        }
    )

    assert response.status == 401
