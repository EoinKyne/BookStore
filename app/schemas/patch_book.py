from pydantic import BaseModel, Field
from typing import Optional


class PatchBook(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
