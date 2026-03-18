import uuid
import logging
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from BookStore.app.models.model import Cart as CartModel
from BookStore.app.models.model import CartItem as CartItemModel
from BookStore.app.models.model import Book as BookModel


logger = logging.getLogger(__name__)


def get_or_create_cart(db: Session,
                       session_id: str):
    logger.debug("Get or create a cart")
    cart = db.query(CartModel).filter(CartModel.session_id == session_id).first()

    if not cart:
        cart = CartModel(session_id=session_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


def add_item(db: Session, cart: CartModel, book_id: uuid, quantity: int):
    logger.debug("Add item to cart")

    if quantity < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Quantity should be at least 1")

    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Book not found")

    if book.stock == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Out of stock")

    item = (db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id,
                                           CartItemModel.book_id == book_id)).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItemModel(cart_id=cart.id, book_id=book_id, quantity=quantity)
        db.add(item)

    db.commit()
    return item