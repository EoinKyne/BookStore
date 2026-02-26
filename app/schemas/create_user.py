from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    roles: list[str]
    username: str
    password: str
    is_active: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "roles": ["string"],
                    "username": "name",
                    "password": "string",
                    "is_active": True
                }
            ]
        }
    }
