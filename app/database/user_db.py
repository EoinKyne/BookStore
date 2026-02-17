from BookStore.app.models.user_model import User
from BookStore.app.auth.auth import get_password_hash


USERS_DB = {
    "admin": User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        is_admin=True,
    ),
    "user": User(
        username="user",
        hashed_password=get_password_hash("user123"),
        is_admin=False,
    ),
}
