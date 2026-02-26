import logging

logger = logging.getLogger(__name__)


def test_create_book_admin(api_request_admin):
    logger.debug("Test create book...")
    response = api_request_admin.post(
        "/books",
        data={
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "price": 10.00,
            "stock": 10
        }
    )
    assert response.status == 200
    body = response.json()
    assert body["title"] == "To Kill a Mockingbird"
    assert body["author"] == "Harper Lee"
    assert body["price"] == 10.00


def test_get_books_admin(api_request_admin):
    logger.debug("Test get books")
    create_response = api_request_admin.post(
        "books",
        data={"title": "1984",
              "author": "George Orwell",
              "price": 14.99,
              "stock": 9})

    response = api_request_admin.get("/books")
    assert response.status == 200
    assert isinstance(response.json(), list)


def test_update_book_with_new_details_admin(api_request_admin):
    logger.debug("Test PUT update on book")
    create_response = api_request_admin.post(
        "books",
        data={"title": "Lord of the Rings",
              "author": "R.R. Tolkien",
              "price": 12.99,
              "stock": 2})
    book_id = create_response.json()["id"]

    response = api_request_admin.put(
        f"/books/{book_id}",
        data={"title": "The Lord of the Rings",
              "author": "J.R.R. Tolkien",
              "price": 17.99,
              "stock": 6}
    )

    assert response.status == 200
    body = response.json()
    assert body["title"] == "The Lord of the Rings"
    assert body["author"] == "J.R.R. Tolkien"
    assert body["price"] == 17.99
    assert body["stock"] == 6


def test_get_book_by_id_admin(api_request_admin):
    logger.debug("Test get book by id")
    create_response = api_request_admin.post(
        "books",
        data={"title": "The Catcher in the Rye",
              "author": "J.D. Salinger",
              "price": 6.00,
              "stock": 19})
    book_id = create_response.json()["id"]

    response = api_request_admin.get(f"/books/{book_id}")
    assert response.status == 200
    body = response.json()
    assert body["id"] == book_id
    assert body["title"] == "The Catcher in the Rye"


def test_delete_of_book(api_request_admin):
    logger.debug("Test delete book by id")
    create_response = api_request_admin.post(
        "books",
        data={"title": "The Great Gatsby",
              "author": " F. Scott Fitzgerald",
              "price": 14.99,
              "stock": 9})
    book_id = create_response.json()["id"]

    response = api_request_admin.delete(f"/books/{book_id}")
    assert response.status == 204


def test_get_book_not_found(api_request_not_authorized):
    logger.debug("Test book not found")
    response = api_request_not_authorized.get(f"/books/99999")
    assert response.status == 404
    assert response.json()["detail"] == "Book not found"


def test_update_of_book_title_author(api_request_admin):
    logger.debug("Test PATCH of book details, author and title")
    create_response = api_request_admin.post(
        "books",
        data={"title": "Lord of the Fly's",
              "author": "Bill Golding",
              "price": 7.99,
              "stock": 6})

    book_id = create_response.json()["id"]

    response = api_request_admin.patch(
        f"/books/{book_id}",
        data={"title": "Lord of the Flies",
              "author": "William Golding"}
    )

    assert response.status == 200
    body = response.json()
    assert body["title"] == "Lord of the Flies"
    assert body["author"] == "William Golding"
    assert body["price"] == 7.99
    assert body["stock"] == 6


def test_update_of_book_prices_stock(api_request_admin):
    logger.debug("Test PATCH of book details, price and stock ")
    create_response = api_request_admin.post(
        "books",
        data={"title": "Animal Farm",
              "author": "George Orwell",
              "price": 14.99,
              "stock": 9})

    book_id = create_response.json()["id"]

    response = api_request_admin.patch(
        f"/books/{book_id}",
        data={"price": 18.99,
              "stock": 19}
    )

    assert response.status == 200
    body = response.json()
    assert body["title"] == "Animal Farm"
    assert body["author"] == "George Orwell"
    assert body["price"] == 18.99
    assert body["stock"] == 19


def test_create_book_invalid_price(api_request_admin):
    logger.debug("Test create book with invalid price ")
    response = api_request_admin.post(
        "books",
        data={"title": "Catch-22",
              "author": "Joseph Heller",
              "price": -14.99,
              "stock": 9})
    assert response.status == 422


def test_create_book_with_incomplete_details(api_request_admin):
    logger.debug("Test create book with invalid details")
    response = api_request_admin.post(
        "books",
        data={"title": "The Grapes of Wrath",
              "price": 14.99
              })
    assert response.status == 422


def test_get_book_not_authorized(api_request_not_authorized, api_request_admin):
    logger.debug("Test get book by id not authorized")
    create_response = api_request_admin.post(
        "books",
        data={"title": "Gone with the Wind",
              "author": "Margaret Mitchell",
              "price": 4.99,
              "stock": 12})
    book_id = create_response.json()["id"]

    response = api_request_not_authorized.get(f"/books/{book_id}")
    assert response.status == 200
    body = response.json()
    assert body["id"] == book_id
    assert body["title"] == "Gone with the Wind"


def test_create_book_not_authorized(api_request_not_authorized):
    logger.debug("Test create book not authorized")
    response = api_request_not_authorized.post(
        "books",
        data={"title": "Slaughterhouse-Five",
              "author": "Kurt Vonnegut Jr.",
              "price": 14.99,
              "stock": 9}
        )
    assert response.status == 401


def test_patch_book_not_authorized(api_request_not_authorized):
    logger.debug("Test patch book not authorized")
    response = api_request_not_authorized.patch(
        f"/books/1",
        data={"title": "One Flew Over the Cuckoo’s Nest",
              "author": "Ken Kesey"}
    )
    assert response.status == 401


def test_put_book_not_authorized(api_request_not_authorized):
    logger.debug("Test put book not authorized")
    response = api_request_not_authorized.put(
        f"/books/1",
        data={"title": "A Clockwork Orange",
              "author": "Anthony Burgess",
              "price": 11.99,
              "stock": 5}
    )
    assert response.status == 401


def test_delete_book_not_authorized(api_request_not_authorized):
    logger.debug("Test delete book not authorized")
    response = api_request_not_authorized.delete(
        f"/books/1"
    )
    assert response.status == 401


def test_create_book_contributor(api_request_contributor):
    logger.debug("Test create book...")
    response = api_request_contributor.post(
        "/books",
        data={
            "title": "Atonement",
            "author": "Ian McEwan",
            "price": 5.99,
            "stock": 14
        }
    )
    assert response.status == 200
    body = response.json()
    assert body["title"] == "Atonement"
    assert body["author"] == "Ian McEwan"
    assert body["price"] == 5.99


def test_get_books_contributor(api_request_contributor):
    logger.debug("Test get books")
    create_response = api_request_contributor.post(
        "books",
        data={"title": "Watchmen",
              "author": "Alan Moore",
              "price": 4.99,
              "stock": 19})

    response = api_request_contributor.get("/books")
    assert response.status == 200
    assert isinstance(response.json(), list)


def test_get_book_by_id_contributor(api_request_contributor):
    logger.debug("Test get book by id contributor")
    create_response = api_request_contributor.post(
        "books",
        data={"title": "Never Let Me Go",
              "author": "Kazuo Ishiguro",
              "price": 4.99,
              "stock": 17})
    book_id = create_response.json()["id"]

    response = api_request_contributor.get(f"/books/{book_id}")
    assert response.status == 200
    body = response.json()
    assert body["id"] == book_id
    assert body["title"] == "Never Let Me Go"


def test_update_book_with_new_details_contributor(api_request_contributor):
    logger.debug("Test PUT update on book")
    create_response = api_request_contributor.post(
        "books",
        data={"title": "Miss Dalloway",
              "author": "Virginia Wolf",
              "price": 12.99,
              "stock": 2})
    book_id = create_response.json()["id"]

    response = api_request_contributor.put(
        f"/books/{book_id}",
        data={"title": "Mrs. Dalloway",
              "author": "Virginia Woolf",
              "price": 11.99,
              "stock": 11}
    )

    assert response.status == 200
    body = response.json()
    assert body["title"] == "Mrs. Dalloway"
    assert body["author"] == "Virginia Woolf"
    assert body["price"] == 11.99
    assert body["stock"] == 11


def test_update_of_book_title_author_contributor(api_request_contributor):
    logger.debug("Test PATCH of book details, author and title contributor")
    create_response = api_request_contributor.post(
        "books",
        data={"title": "Invisible ",
              "author": "Ralph Ellison",
              "price": 6.00,
              "stock": 4})

    book_id = create_response.json()["id"]

    response = api_request_contributor.patch(
        f"/books/{book_id}",
        data={"title": "Invisible Man",
              "author": "Ralph Ellison"}
    )

    assert response.status == 200
    body = response.json()
    assert body["title"] == "Invisible Man"
    assert body["author"] == "Ralph Ellison"
    assert body["price"] == 6.00
    assert body["stock"] == 4


def test_update_of_book_prices_stock_contributor(api_request_contributor):
    logger.debug("Test PATCH of book details, price and stock contributor ")
    create_response = api_request_contributor.post(
        "books",
        data={"title": "How to catch sharks",
              "author": "Robert Shaw",
              "price": 14.99,
              "stock": 9})

    book_id = create_response.json()["id"]

    response = api_request_contributor.patch(
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


def test_create_book_invalid_price_contributor(api_request_contributor):
    logger.debug("Test create book with invalid price contributor")
    response = api_request_contributor.post(
        "books",
        data={"title": "How to catch sharks",
              "author": "Robert Shaw",
              "price": -14.99,
              "stock": 9})
    assert response.status == 422


def test_create_book_with_incomplete_details_contributor(api_request_contributor):
    logger.debug("Test create book with invalid details contributor")
    response = api_request_contributor.post(
        "books",
        data={"title": "How to catch sharks",
              "price": 14.99
              })
    assert response.status == 422
