from pydantic import BaseModel


class UpdateIsActiveUser(BaseModel):
    is_active: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "is_active": False,
                }
            ]
        }
    }


class UpdatePass(BaseModel):
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "password": "new pass"
            }]
        }
    }