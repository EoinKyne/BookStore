from pydantic import BaseModel
from uuid import UUID


class AddCartItem(BaseModel):
    book_id: UUID
    quantity: int


class CartItemResponse(BaseModel):
    book_id: UUID
    quantity: int


class CheckoutResponse(BaseModel):
    order_id: UUID
    total: float
