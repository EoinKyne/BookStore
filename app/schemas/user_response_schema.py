from uuid import UUID

from pydantic import BaseModel

from BookStore.app.schemas.role_response_schema import RoleResponse


class UserResponse(BaseModel):
    id: UUID
    username: str
    is_active: bool
    roles: list[RoleResponse]

    model_config = {
        "from_attributes": True
    }