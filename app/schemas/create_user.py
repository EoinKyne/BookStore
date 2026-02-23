from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    role: str
    username: str
    hashed_password: str
    is_active: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "Contributor",
                    "username": "name",
                    "password": "string",
                    "is_active": True
                }
            ]
        }
    }
