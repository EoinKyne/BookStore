from pydantic import BaseModel


class CreateUser(BaseModel):

    role: str
    username: str
    hashed_password: str
    is_active: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "Administrator",
                    "username": "name",
                    "password": "string",
                    "is_active": "true or false",
                }
            ]
        }
    }
