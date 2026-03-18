import pytest
import logging
import uuid
from fastapi import HTTPException, status
from BookStore.app.models.model import Book as BookModel
from BookStore.app.models.model import Cart as CartModel
from BookStore.app.models.model import CartItem as CartItemModel
from BookStore.app.models.model import CheckoutSession as CheckoutSessionModel
from BookStore.app.services import checkout_service

logger = logging.getLogger(__name__)



def test_create_checkout_session(db_session):
    logger.debug("Test create session with a user id")
    new_book = BookModel(
        title="Snow Crash",
        author="Neal Stephenson",
        price=16.50,
        stock=7,
    )

    db_session.add(new_book)
    db_session.commit()
    db_session.refresh(new_book)

    test_cart = CartModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    db_session.add(test_cart)
    db_session.commit()
    db_session.refresh(test_cart)

    db_book = db_session.query(BookModel).filter(BookModel.title == new_book.title).first()
    empty_cart = db_session.query(CartModel).filter(CartModel.id == test_cart.id).first()

    test_item = CartItemModel(
        id=uuid.uuid4(),
        cart_id=empty_cart.id,
        book_id=db_book.id,
        quantity=1
    )

    db_session.add(test_item)
    db_session.commit()
    db_session.refresh(test_item)

    cart = db_session.query(CartModel).filter(CartModel.id == test_cart.id).first()

    session = checkout_service.create_checkout_session(db_session, test_cart.session_id)

    assert session is not None
    assert session.cart_id == cart.id
    assert session.user_id == test_cart.user_id


def test_no_checkout_session_created_when_no_cart_exists(db_session):
    logger.debug("Test no checkout session created when cart does not exist")
    new_book = BookModel(
        title="White Noise",
        author="Don DeLillo",
        price=6.50,
        stock=5,
    )

    db_session.add(new_book)
    db_session.commit()
    db_session.refresh(new_book)

    with pytest.raises(HTTPException) as exe_info:
        session = checkout_service.create_checkout_session(db_session, uuid.uuid4())

    assert exe_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exe_info.value.detail == "No cart exists"


def test_no_checkout_session_is_created_with_empty_cart(db_session):
    logger.debug("Test empty cart returns with exception")
    test_cart = CartModel(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
    )

    db_session.add(test_cart)
    db_session.commit()
    db_session.refresh(test_cart)
    cart = db_session.query(CartModel).filter(CartModel.id == test_cart.id).first()

    with pytest.raises(HTTPException) as exc_info:
        session = checkout_service.create_checkout_session(db_session, test_cart.session_id)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Cart is empty"


def test_handle_payment_success(db_session):
    logger.debug("Test handle payment success")
    new_book = BookModel(
        title="The Prime of Miss Jean Brodie",
        author="Muriel Spark",
        price=12.00,
        stock=9,
    )

    db_session.add(new_book)
    db_session.commit()
    db_session.refresh(new_book)

    test_cart = CartModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    db_session.add(test_cart)
    db_session.commit()
    db_session.refresh(test_cart)

    db_book = db_session.query(BookModel).filter(BookModel.title == new_book.title).first()
    cart = db_session.query(CartModel).filter(CartModel.id == test_cart.id).first()

    test_item = CartItemModel(
        id=uuid.uuid4(),
        cart_id=cart.id,
        book_id=db_book.id,
        quantity=1
    )

    db_session.add(test_item)
    db_session.commit()
    db_session.refresh(test_item)

    test_checkout_session = CheckoutSessionModel(
        cart_id=cart.id,
        user_id=None,
        total_price=12.00,
        status="CREATED",
        payment_provider="twostripes",
    )
    db_session.add(test_checkout_session)
    db_session.commit()
    db_session.refresh(test_checkout_session)

    order = checkout_service.handle_payment_success(db_session, test_checkout_session.id)

    assert order.status == "PAID"
    assert order.items[0].book_id == db_book.id


def test_order_creation_reduces_book_stock_by_quantity(db_session):
    logger.debug("Test order creation reduces book stock by quantity")
    new_book = BookModel(
        title="Neuromancer (Sprawl #1)",
        author="William Gibson",
        price=11.00,
        stock=9,
    )

    db_session.add(new_book)
    db_session.commit()
    db_session.refresh(new_book)

    test_cart = CartModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    db_session.add(test_cart)
    db_session.commit()
    db_session.refresh(test_cart)

    db_book = db_session.query(BookModel).filter(BookModel.title == new_book.title).first()
    cart = db_session.query(CartModel).filter(CartModel.id == test_cart.id).first()

    test_item = CartItemModel(
        id=uuid.uuid4(),
        cart_id=cart.id,
        book_id=db_book.id,
        quantity=1
    )

    db_session.add(test_item)
    db_session.commit()
    db_session.refresh(test_item)

    test_checkout_session = CheckoutSessionModel(
        cart_id=cart.id,
        user_id=None,
        total_price=12.00,
        status="CREATED",
        payment_provider="twostripes",
    )
    db_session.add(test_checkout_session)
    db_session.commit()
    db_session.refresh(test_checkout_session)

    order = checkout_service.handle_payment_success(db_session, test_checkout_session.id)

    assert order.status == "PAID"
    assert order.items[0].book_id == db_book.id
    assert db_book.stock == 8


def test_multiple_items_order_creation(db_session):
    logger.debug("Test multiple item order creation")
    book_one = BookModel(
        title="Red Harvest (The Continental Op #1)",
        author="Dashiell Hammett",
        price=10.00,
        stock=9,
    )
    book_two = BookModel(
        title="The Corrections",
        author=" Jonathan Franzen",
        price=11.00,
        stock=5,
    )


    db_session.add(book_one)
    db_session.add(book_two)
    db_session.commit()
    db_session.refresh(book_one)
    db_session.refresh(book_two)

    test_cart = CartModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    db_session.add(test_cart)
    db_session.commit()
    db_session.refresh(test_cart)

    db_book_one = db_session.query(BookModel).filter(BookModel.title == book_one.title).first()
    db_book_two = db_session.query(BookModel).filter(BookModel.title == book_two.title).first()
    cart = db_session.query(CartModel).filter(CartModel.id == test_cart.id).first()

    item_one = CartItemModel(
        id=uuid.uuid4(),
        cart_id=cart.id,
        book_id=db_book_one.id,
        quantity=1
    )

    item_two = CartItemModel(
        id=uuid.uuid4(),
        cart_id=cart.id,
        book_id=db_book_two.id,
        quantity=2
    )

    db_session.add(item_one)
    db_session.add(item_two)
    db_session.commit()
    db_session.refresh(item_one)
    db_session.refresh(item_two)

    test_checkout_session = CheckoutSessionModel(
        cart_id=cart.id,
        user_id=None,
        total_price=32.00,
        status="CREATED",
        payment_provider="twostripes",
    )
    db_session.add(test_checkout_session)
    db_session.commit()
    db_session.refresh(test_checkout_session)

    order = checkout_service.handle_payment_success(db_session, test_checkout_session.id)

    assert order.status == "PAID"
    assert order.items[0].book_id == db_book_one.id
    assert order.items[1].book_id == db_book_two.id
    assert db_book_one.stock == 8
    assert db_book_two.stock == 3