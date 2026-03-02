import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from BookStore.app.models.model import Book as BookModel
from BookStore.app.schemas.create_book import CreateBook
from BookStore.app.schemas.patch_book import PatchBook

logger = logging.getLogger(__name__)


def get_book_or_404(db: Session, book_id: int) -> BookModel:
    logger.debug("Get book by id")
    book = db.get(BookModel, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


def create_book(db: Session, book: CreateBook) -> BookModel:
    logger.debug("Create new book")
    db_book = BookModel(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, data: CreateBook) -> BookModel:
    logger.debug("Update all details of book")

    book = get_book_or_404(db, book_id)

    for field, value in data.model_dump().items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)

    return book


def delete_book(db: Session, book_id: int) -> 204:
    logger.debug("Delete book")
    book = get_book_or_404(db, book_id)
    db.delete(book)
    db.commit()


def get_books(db: Session,
              limit: int,
              offset: int,
              author: str | None = None):
    logger.debug("Get books")
    books = db.query(BookModel).order_by(BookModel.id.desc())

    if author:
        books = books.filter(BookModel.author.ilike(f"%{author}%"))

    return books.offset(offset).limit(limit).all()


def patch_book(db: Session, book_id: int, data: PatchBook):
    logger.debug("Patch book")
    book = get_book_or_404(db, book_id)

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book
