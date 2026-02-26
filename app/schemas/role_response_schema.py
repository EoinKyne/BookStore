from pydantic import BaseModel


class RoleResponse(BaseModel):
    name: str

    model_config = {
        "from_attributes": True
    }
