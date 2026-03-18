import logging
import uuid

import pytest
from fastapi import HTTPException, status
from uuid import UUID

from BookStore.app.models.model import Book as BookModel
from BookStore.app.schemas.create_book import CreateBook
from BookStore.app.schemas.patch_book import PatchBook
from BookStore.app.services import book_service

logger = logging.getLogger(__name__)


def test_get_book_or_404(db_session):
    logger.debug("Test get book")

    test_book = BookModel(
        title="Never Let Me Go",
        author="Kazuo Ishiguro",
        price=4.99,
        stock=17,
    )

    db_session.add(test_book)
    db_session.commit()
    db_session.refresh(test_book)

    book = db_session.query(BookModel).filter(BookModel.title == "Never Let Me Go").first()

    result = book_service.get_book_or_404(db_session, book.id)

    assert result == book
    assert result.title == book.title


def test_get_book_or_404_not_found(db_session):
    logger.debug("Test get book that does not exist")

    with pytest.raises(HTTPException) as exc_info:
        book_service.get_book_or_404(db_session, uuid.uuid4())
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_create_book(db_session):
    logger.debug("Test create new book")
    new_book = CreateBook(
        title="Possession",
        author="A.S. Byatt",
        price=12.50,
        stock=11,
    )

    result = book_service.create_book(db_session, new_book)

    book = db_session.query(BookModel).filter(BookModel.title == "Possession").first()

    assert result.title == book.title
    assert result.author == book.author
    assert result.author == "A.S. Byatt"


def test_update_book(db_session):
    logger.debug("Test update all details of book")

    new_book = CreateBook(
        title="A Passage too India",
        author="E.M. forster",
        price=7.50,
        stock=19,
    )
    db_book = BookModel(**new_book.model_dump())
    db_session.add(db_book)
    db_session.commit()
    db_session.refresh(db_book)

    update_book = db_session.query(BookModel).filter(BookModel.title == "A Passage too India").first()

    data = CreateBook(
        title="A Passage to India",
        author="E.M. Forster",
        price=17.50,
        stock=19,
    )

    result = book_service.update_book(db_session, update_book.id, data)

    assert result.title == "A Passage to India"
    assert result.author == "E.M. Forster"
    assert result.author != "E.M. forster"
    assert result.price == 17.50
    assert result.stock == 19


def test_delete_book(db_session):
    logger.debug("Test delete book")
    new_book = CreateBook(
        title="The Sound and the Fury",
        author="William Faulkner",
        price=12.50,
        stock=9,
    )
    db_book = BookModel(**new_book.model_dump())
    db_session.add(db_book)
    db_session.commit()
    db_session.refresh(db_book)

    update_book = db_session.query(BookModel).filter(BookModel.title == "The Sound and the Fury").first()
    result = book_service.delete_book(db_session, update_book.id)

    assert result is None


def test_get_books(db_session):
    logger.debug("Test get books")

    books = book_service.get_books(db_session, 10, 0, "")

    assert isinstance(books, list)


def test_det_books_by_author(db_session):
    logger.debug("Test get books by author")
    new_book = CreateBook(
        title="The Heart Is a Lonely Hunter",
        author="Carson McCullers",
        price=7.50,
        stock=8,
    )
    db_book = BookModel(**new_book.model_dump())
    db_session.add(db_book)
    db_session.commit()
    db_session.refresh(db_book)

    book = book_service.get_books(db_session, 10, 0, "Carson McCullers")

    assert isinstance(book, list)
    assert book[0].author == "Carson McCullers"



def test_patch_books(db_session):
    logger.debug("Test patch book")
    new_book = CreateBook(
        title="I, Claudius",
        author="Robert Graves",
        price=14.50,
        stock=10,
    )
    db_book = BookModel(**new_book.model_dump())
    db_session.add(db_book)
    db_session.commit()
    db_session.refresh(db_book)

    update_book = db_session.query(BookModel).filter(BookModel.title == "I, Claudius").first()

    data = PatchBook(
        title="I, Claudius (Claudius, #1)",
        price=12.50,
    )

    result = book_service.patch_book(db_session, update_book.id, data)

    assert result.title == "I, Claudius (Claudius, #1)"
    assert result.price == 12.50
