from fastapi import APIRouter, HTTPException, Depends, Query
from BookStore.app.schemas.book import Book
from sqlalchemy.orm import Session
from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.models.model import Book as BookModel
from BookStore.app.schemas.create_book import CreateBook
from BookStore.app.schemas.patch_book import PatchBook
from BookStore.app.dependencies.usr_dependencies import get_current_user_oauth2
from BookStore.app.models.user_model import User

import logging


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[Book])
def get_books(db: Session = Depends(get_db),
              limit: int = Query(10, ge=1, le=100),
              offset: int = Query(0, ge=0),
              author: str | None = None):
    logger.info("Get books...")

    books = db.query(BookModel).order_by(BookModel.id.desc())

    if author:
        books = books.filter(BookModel.author.ilike(f"%{author}%"))

    return books.offset(offset).limit(limit).all()


@router.get("/{book_id}", response_model=Book)
def get_book(book_id: int,
             db: Session = Depends(get_db)):
    logger.info(f"Get books by id {book_id}")
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=Book)
def create_book(book: CreateBook,
                db: Session = Depends(get_db),
                user: User = Depends(get_current_user_oauth2)):
    logger.info(f"Adding new book... {book}")
    db_book = BookModel(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.put("/{book_id}", response_model=Book)
def update_book(book_id: int,
                book_data: CreateBook,
                db: Session = Depends(get_db),
                user: User = Depends(get_current_user_oauth2)):
    logger.info(f"Updating all book details... {book_data}")
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in book_data.dict().items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int,
                db: Session = Depends(get_db),
                user: User = Depends(get_current_user_oauth2)):
    logger.info(f"Deleting book id {book_id}")
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()


@router.patch("/{book_id}", response_model=Book)
def patch_book(
        book_id: int,
        data: PatchBook,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user_oauth2)
):
    logger.info(f"Updating book for details {data}")
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not Book:
        raise HTTPException(status_code=404, detail="Book not found")

    updates = data.dict(exclude_unset=True)

    for field, value in updates.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book
