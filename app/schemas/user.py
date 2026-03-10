from uuid import UUID

from BookStore.app.schemas.create_user import CreateUser


class User(CreateUser):
    id: UUID
