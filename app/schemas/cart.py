from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class AddCartItem(BaseModel):
    book_id: UUID
    quantity: int = Field(..., gt=0, description="Must be a positive value")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "book_id": "ff33729d-f6ad-42cd-9feb-5a6117f246a1",
                    "quantity": 1
                }
            ]
        }
    }


class CartItemResponse(BaseModel):
    book_id: UUID
    quantity: int

    model_config = {
        "from_attributes": True
    }


class CheckoutResponse(BaseModel):
    order_id: UUID
    total: Decimal

    model_config = {
        "from_attributes": True
    }
