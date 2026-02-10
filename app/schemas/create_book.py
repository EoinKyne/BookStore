from pydantic import BaseModel, Field


class CreateBook(BaseModel):
    title: str
    author: str
    price: float = Field(..., gt=0, description="Price must positive", example="12.99")
    stock: int = Field(..., ge=0, )

