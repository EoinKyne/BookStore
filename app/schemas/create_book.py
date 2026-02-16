from pydantic import BaseModel, Field


class CreateBook(BaseModel):
    title: str
    author: str
    price: float = Field(..., gt=0, description="Price must positive")
    stock: int = Field(..., ge=0, )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Book Title",
                    "author": "Book Author",
                    "price": 12.99,
                    "stock": 1
                }
            ]
        }
    }
