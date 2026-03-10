import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.dependencies.usr_dependencies import requre_permission
from BookStore.app.models.model import User
from BookStore.app.schemas.book import Book
from BookStore.app.schemas.create_book import CreateBook
from BookStore.app.schemas.patch_book import PatchBook
from BookStore.app.services import book_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[Book])
def get_books(db: Session = Depends(get_db),
              limit: int = Query(10, ge=1, le=100),
              offset: int = Query(0, ge=0),
              author: str | None = None):
    logger.info("Get books...")
    books = book_service.get_books(db, limit, offset, author)
    return books


@router.get("/{book_id}", response_model=Book)
def get_book(book_id: UUID,
             db: Session = Depends(get_db)):
    logger.debug(f"Get books by id")
    book = book_service.get_book_or_404(db, book_id)
    return book


@router.post("/", response_model=Book)
def create_book(book: CreateBook,
                db: Session = Depends(get_db),
                user: User = Depends(requre_permission("book:create"))):
    logger.info(f"Adding new book...")
    db_book = book_service.create_book(db, book)

    return db_book


@router.put("/{book_id}", response_model=Book)
def update_book(book_id: UUID,
                book_data: CreateBook,
                db: Session = Depends(get_db),
                user: User = Depends(requre_permission("book:update"))):
    logger.info(f"Updating book details...")
    book = book_service.update_book(db, book_id, book_data)

    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: UUID,
                db: Session = Depends(get_db),
                user: User = Depends(requre_permission("book:delete"))):
    logger.info(f"Deleting book id {book_id}")
    book_service.delete_book(db, book_id)


@router.patch("/{book_id}", response_model=Book)
def patch_book(
        book_id: UUID,
        data: PatchBook,
        db: Session = Depends(get_db),
        user: User = Depends(requre_permission("book:update"))
):
    logger.info(f"Updating book for details {data}")
    book = book_service.patch_book(db, book_id, data)
    '''
    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    '''
    return book
