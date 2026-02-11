import pytest


def test_create_book(api_request):
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
    response = api_request.get("/books")
    assert response.status == 200
    assert isinstance(response.json(), list)


def test_get_book(api_request):
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
    assert response.status == 200
    body = response.json()
    assert body["id"] == book_id
    assert body["title"] == "How to catch sharks"
