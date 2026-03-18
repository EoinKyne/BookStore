from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class PatchBook(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
