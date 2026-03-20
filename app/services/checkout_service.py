import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from BookStore.app.models.model import Book as BookModel
from BookStore.app.models.model import Cart as CartModel
from BookStore.app.models.model import CheckoutSession as CheckoutSessionModel
from BookStore.app.models.model import Order as OrderModel
from BookStore.app.models.model import OrderItem as OrderItemModel
from BookStore.app.services.cart_service import remove_expired_items

logger = logging.getLogger(__name__)


def create_checkout_session(db: Session, sess_id: str):
    logger.debug("Create checkout session")

    cart = db.query(CartModel).filter(CartModel.session_id == sess_id).first()

    if not cart:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No cart exists")

    if not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cart is empty")

    expired_items = remove_expired_items(cart)

    if expired_items:
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Some items expired. Please review your cart")

    total = 0

    for item in cart.items:
        book = db.get(BookModel, item.book_id)
        total += book.price * item.quantity

    session = CheckoutSessionModel(
        cart_id=cart.id,
        user_id=cart.user_id,
        total_price=total,
        status="CREATED",
        payment_provider="twostripes"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def handle_payment_success(db: Session, checkout_session_id: str):
    session = db.get(CheckoutSessionModel, checkout_session_id)

    cart = session.cart

    order = OrderModel(
        user_id=session.user_id,
        checkout_session_id=session.id,
        status="PAID",
        total_price=session.total_price,
    )

    for item in cart.items:
        book = db.get(BookModel, item.book_id)

        order.items.append(
            OrderItemModel(
                book_id=book.id,
                quantity=item.quantity,
                price=book.price,
            )
        )

        book.stock -= item.quantity

    db.add(book)
    db.add(order)

    session.status = "PAID"

    cart.items.clear()
    db.commit()
    return order