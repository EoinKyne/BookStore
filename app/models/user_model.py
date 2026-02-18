from pydantic import BaseModel


class User(BaseModel):
    username: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
