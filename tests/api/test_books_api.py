import pytest
from playwright.sync_api import APIRequestContext

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture
def api_request(playwright) -> APIRequestContext:
    request_context = playwright.request.new_context(
        base_url=BASE_URL
    )
    yield request_context
    request_context.dispose()


def test_create_book(api_request: APIRequestContext):
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


def test_get_books(api_request: APIRequestContext):
    response = api_request.get("/books")
    assert response.status == 200
    assert isinstance(response.json(), list)

def test_get_book(api_request: APIRequestContext):
    create_response = api_request.post(
        "books",
        data={"title": "How to catch sharks",
            "author": "Robert Shaw",
            "price": 14.99,
            "stock": 9})
    book_id = create_response.json()["id"]
    print(book_id)

    response = api_request.get(f"/books/{book_id}")
    print(response)
    #assert response.status == 200
    #body = response.json()
    #assert body["id"] == book_id
    #assert body["title"] == "How to catch sharks"
