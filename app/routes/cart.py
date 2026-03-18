import logging
import uuid

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.schemas.cart import AddCartItem, CheckoutResponse
from BookStore.app.services import cart_service
from BookStore.app.services import checkout_service
from BookStore.app.models.model import Cart

router = APIRouter()


logger = logging.getLogger(__name__)


def get_session_id(request: Request, response: Response):
    logger.info("Get session id")
    session_id = request.cookies.get("cart_session")

    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie("cart_session", session_id)

    return session_id


@router.post("/items")
def add_to_cart(item: AddCartItem,
                request: Request,
                response: Response,
                db: Session = Depends(get_db)):
    logger.info("Add item to cart")
    session_id = get_session_id(request, response)
    cart = cart_service.get_or_create_cart(db, session_id)
    cart_service.add_item(db, cart, item.book_id, item.quantity)

    return {"message": f"item added. cart has {len(cart.items)} item(s) added"}


@router.post("/checkout", response_model=CheckoutResponse)
def checkout_cart(request: Request,
                  response: Response,
                  db: Session = Depends(get_db)):
    logger.info("Checkout cart")
    session_id = get_session_id(request, response)
    checkout_session = checkout_service.create_checkout_session(db,session_id)
    order = checkout_service.handle_payment_success(db, checkout_session.id)

    return CheckoutResponse(order_id=order.id,
                            total=order.total_price)



#BookStore\app\routes\auth_routes.py                    20      7    65%   21-27
#BookStore\app\routes\books.py                          43     18    58%   24-26, 32-34, 41-44, 52-55, 62-63, 73-84
#BookStore\app\routes\cart.py                           30     15    50%   19-26, 34-39, 46-50
#BookStore\app\routes\users.py                          53     23    57%   24-27, 35-39, 46-49, 56-60, 68-71, 79-82, 90-93, 100-102
