import logging
import re
import uuid

import pytest
from fastapi import Response
from BookStore.app.routes.cart import get_session_id

logger = logging.getLogger(__name__)


def test_cart_generates_session_if_missing(api_request_contributor, api_request_not_authorized):
    logger.debug("Test cart generates a session id if missing")

    book = api_request_contributor.post(
        "books",
        data={"title": "Naked Lunch: The Restored Text",
              "author": "William S. Burroughs",
              "price": 5.99,
              "stock": 9
              }
    )

    book_id = book.json()["id"]

    response = api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": book_id,
            "quantity": 1
        }
    )

    assert response.status == 200
    cookies = response.headers.get("set-cookie")
    assert "cart_session=" in cookies
    cookie_header = response.headers["set-cookie"]
    session_id = re.search(r"cart_session=([^;]+)", cookie_header).group(1)
    uuid.UUID(session_id)


def test_cart_reuse_session(api_request_contributor, api_request_not_authorized):
    logger.debug("Test cart reuses session")
    book = api_request_contributor.post(
        "books",
        data={"title": "Revolutionary Road",
              "author": "Richard Yates",
              "price": 9.99,
              "stock": 4
              }
    )

    book_id = book.json()["id"]

    api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": book_id,
            "quantity": 1
        }
    )

    cookies_first = api_request_not_authorized.storage_state()["cookies"]
    session_first = next(c for c in cookies_first if c["name"] == "cart_session")["value"]

    response = api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": book_id,
            "quantity": 2
        }
    )

    cookies_second = api_request_not_authorized.storage_state()["cookies"]
    session_second = next(c for c in cookies_second if c["name"] == "cart_session")["value"]

    assert response.status == 200
    assert session_first == session_second


def test_add_to_cart(api_request_contributor, api_request_not_authorized):
    logger.debug("Test get cart session cookies")

    book = api_request_contributor.post(
        "books",
        data={"title": "The Blind Assassin",
              "author": "Margaret Atwood",
              "price": 4.99,
              "stock": 19
        }
    )

    book_id = book.json()["id"]

    response = api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": book_id,
            "quantity": 1
        }
    )

    assert response.status == 200
    body = response.json()
    assert body["message"] == "item added. cart has 1 item(s) added"


def test_add_multiple_items_to_cart(api_request_contributor, api_request_not_authorized):
    logger.debug("Test add multiple items to cart")

    book_first = api_request_contributor.post(
        "books",
        data={"title": "The Bridge of San Luis Rey ",
              "author": "Thornton Wilder",
              "price": 4.99,
              "stock": 19
              }
    )

    book_id_first = book_first.json()["id"]


    book_second = api_request_contributor.post(
        "books",
        data={"title": "American Pastoral",
              "author": "Philip Roth",
              "price": 11.99,
              "stock": 3
              }
    )

    book_id_second = book_second.json()["id"]

    api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": book_id_first,
            "quantity": 1
        }
    )

    response = api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": book_id_second,
            "quantity": 2
        }
    )

    assert response.status == 200
    body = response.json()
    assert body["message"] == "item added. cart has 2 item(s) added"


def test_add_to_cart_invalid_quantity(api_request_contributor, api_request_not_authorized):
    logger.debug("Test add to cart with invalid quantity")

    book = api_request_contributor.post(
        "books",
        data={"title": "The Power and the Glory",
              "author": "Graham Greene",
              "price": 13.99,
              "stock": 5
              }
    )

    book_id = book.json()["id"]

    response = api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id":book_id,
            "quantity": -1,
        }
    )

    assert response.status == 422


def test_add_to_cart_book_stock_is_zero(api_request_contributor, api_request_not_authorized):
    logger.debug("Test add to cart with book stock of 0")

    book = api_request_contributor.post(
        "books",
        data={"title": "The Crying of Lot 49",
              "author": "Thomas Pynchon",
              "price": 11.99,
              "stock": 0
              }
    )

    book_id = book.json()["id"]

    response = api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": book_id,
            "quantity": 1,
        }
    )

    assert response.status == 400
    assert response.json()["detail"] == "Out of stock"


def test_add_to_cart_where_book_does_not_exist(api_request_not_authorized):
    logger.debug("Test checkout order")

    response = api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": str(uuid.uuid4()),
            "quantity": 1,
        }
    )

    assert response.status == 404
    assert response.json()["detail"] == "Book not found"


def test_checkout_cart(api_request_contributor, api_request_not_authorized):
    logger.debug("Test checkout of cart")

    book = api_request_contributor.post(
        "books",
        data={"title": "Under the Volcano",
              "author": "Malcolm Lowry",
              "price": 14.99,
              "stock": 10
              }
    )

    book_id = book.json()["id"]

    add_to_cart = api_request_not_authorized.post(
        "/cart/items",
        data={
            "book_id": book_id,
            "quantity": 1,
        }
    )

    response = api_request_not_authorized.post(
        "/cart/checkout",
    )

    assert response.status == 200
    body = response.json()
    assert body["total"] == '14.99'


def test_checkout_service_empty_cart(api_request_not_authorized):
    logger.debug("Test checkout with empty cart")

    response = api_request_not_authorized.post(
        "/cart/checkout",
    )

    assert response.status == 400
    body = response.json()
    assert body["detail"] == "No cart exists"
