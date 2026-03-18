import uuid

import pytest
import logging
from uuid import UUID
from fastapi import Request, HTTPException, status
from BookStore.app.models.model import Cart as CartModel
from BookStore.app.models.model import CartItem as CartItemModel
from BookStore.app.models.model import Book as BookModel
from BookStore.app.schemas.create_book import CreateBook
from BookStore.app.services import cart_service


logger = logging.getLogger(__name__)


def test_get_cart(db_session):
    logger.debug("Test get cart")
    test_cart = CartModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    db_session.add(test_cart)
    db_session.commit()
    db_session.refresh(test_cart)

    cart_in_db = db_session.query(CartModel).filter(CartModel.session_id == test_cart.session_id).first()

    cart = cart_service.get_or_create_cart(db_session, str(cart_in_db.session_id))

    assert cart.id == test_cart.id
    assert cart.user_id == test_cart.user_id
    assert cart.session_id == test_cart.session_id


def test_create_cart(db_session):
    logger.debug("Test create cart")

    cart = cart_service.get_or_create_cart(db_session, 'ac09dead-bf54-4f9d-a375-13e270bc7387')

    assert cart is not None


def test_add_item_to_cart(db_session):
    logger.debug("Test add item to cart")

    new_book = BookModel(
        title="Their Eyes Were Watching God",
        author=" Zora Neale Hurston",
        price=9.50,
        stock=11,
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

    item = cart_service.add_item(db_session, cart, db_book.id, 2)

    assert item.quantity == 3


def test_add_item_no_item_in_cart(db_session):
    logger.debug("Test add item to cart with no items in cart")

    new_book = BookModel(
        title="All the King's Men",
        author="Robert Penn Warren",
        price=17.50,
        stock=3,
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

    item = cart_service.add_item(db_session, cart, db_book.id, 1)

    assert item is not None
    assert type(item) is CartItemModel
    assert item.quantity == 1


def test_add_item_to_cart_invalid_quantity(db_session):
    logger.debug("Test add item to cart with invalid quantity")

    new_book = BookModel(
        title="Portnoy’s Complaint",
        author=" Philip Roth",
        price=7.50,
        stock=3,
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

    with pytest.raises(HTTPException) as exc_info:
        item = cart_service.add_item(db_session, cart, db_book.id, 0)

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert exc_info.value.detail == "Quantity should be at least 1"


def test_add_item_to_cart_item_does_not_exist(db_session):
    logger.debug("Test add book that does not exist to cart")

    test_cart = CartModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    db_session.add(test_cart)
    db_session.commit()
    db_session.refresh(test_cart)

    with pytest.raises(HTTPException) as exc_info:
        item = cart_service.add_item(db_session, test_cart, str(uuid.uuid4()), 1)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Book not found"


def test_add_item_to_cart_with_stock_of_zero(db_session):
    logger.debug("Test add book to cart with stock of zero")

    new_book = BookModel(
        title="Wide Sargasso Sea",
        author="Jean Rhys",
        price=8.50,
        stock=0,
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

    with pytest.raises(HTTPException) as exc_info:
        item = cart_service.add_item(db_session, cart, db_book.id, 1)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Out of stock"


