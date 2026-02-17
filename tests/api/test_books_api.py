import pytest
import logging

logger = logging.getLogger(__name__)


def test_create_book(api_request):
    logger.info("Test create book...")
    response = api_request.post(
        "/books",
        data={
            "title": "Clean Code",
            "author": "Robert Martin",
            "price": 35.99,
            "stock": 10
        }
    )
    assert response.status == 200
    body = response.json()
    assert body["title"] == "Clean Code"
    assert body["author"] == "Robert Martin"
    assert body["price"] == 35.99


def test_get_books(api_request):
    logger.info("Test get books")
    create_response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
              "author": "Robert Shaw",
              "price": 14.99,
              "stock": 9})

    response = api_request.get("/books")
    assert response.status == 200
    assert isinstance(response.json(), list)


def test_get_book(api_request):
    logger.info("Test get book by id")
    create_response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
            "author": "Robert Shaw",
            "price": 14.99,
            "stock": 9})
    book_id = create_response.json()["id"]

    response = api_request.get(f"/books/{book_id}")
    assert response.status == 200
    body = response.json()
    assert body["id"] == book_id
    assert body["title"] == "How to catch sharks"


def test_get_book_not_found(api_request):
    logger.info("Test book not foune")
    response = api_request.get(f"/books/99")
    assert response.status == 404
    assert response.json()["detail"] == "Book not found"


def test_get_book_invalid_price(api_request):
    logger.info("Test create book with invalid price ")
    response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
              "author": "Robert Shaw",
              "price": -14.99,
              "stock": 9})
    assert response.status == 422


def test_create_book_with_incomplete_details(api_request):
    logger.info("Test create book with invalid details")
    response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
              "price": 14.99
              })
    assert response.status == 422


def test_update_book_with_new_details(api_request):
    logger.debug("Test PUT update on book")
    create_response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
              "author": "Robert Shaw",
              "price": 14.99,
              "stock": 9})
    book_id = create_response.json()["id"]

    response = api_request.put(
        f"/books/{book_id}",
        data={"title": "How to catch sharks the prequel",
              "author": "Robert Shaw",
              "price": 17.99,
              "stock": 6}
    )

    assert response.status == 200
    body = response.json()
    assert body["title"] == "How to catch sharks the prequel"
    assert body["author"] == "Robert Shaw"
    assert body["price"] == 17.99
    assert body["stock"] == 6


def test_delete_of_book(api_request):
    logger.debug("Test delete book by id")
    create_response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
              "author": "Robert Shaw",
              "price": 14.99,
              "stock": 9})
    book_id = create_response.json()["id"]

    response = api_request.delete(f"/books/{book_id}")
    assert response.status == 204


def test_update_of_book_title_author(api_request):
    logger.debug("Test PATCH of book details, author and title")
    create_response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
              "author": "Robert Shaw",
              "price": 14.99,
              "stock": 9})

    book_id = create_response.json()["id"]

    response = api_request.patch(
        f"/books/{book_id}",
        data={"title": "How to catch sharks the prequel",
              "author": "Robert Shaw III"}
    )

    assert response.status == 200
    body = response.json()
    assert body["title"] == "How to catch sharks the prequel"
    assert body["author"] == "Robert Shaw III"
    assert body["price"] == 14.99
    assert body["stock"] == 9


def test_update_of_book_prices_stock(api_request):
    logger.debug("Test PATCH of book details, price and stock ")
    create_response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
              "author": "Robert Shaw",
              "price": 14.99,
              "stock": 9})

    book_id = create_response.json()["id"]

    response = api_request.patch(
        f"/books/{book_id}",
        data={"price": 18.99,
              "stock": 19}
    )

    assert response.status == 200
    body = response.json()
    assert body["title"] == "How to catch sharks"
    assert body["author"] == "Robert Shaw"
    assert body["price"] == 18.99
    assert body["stock"] == 19
