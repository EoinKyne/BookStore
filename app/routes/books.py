from fastapi import APIRouter, HTTPException, Depends
from BookStore.app.schemas.book import Book
from BookStore.app.schemas.create_book import CreateBook
from sqlalchemy.orm import Session
from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.models.model import Book as BookModel

router = APIRouter()


@router.get("/", response_model=list[Book])
def get_books(db: Session = Depends(get_db)):
    return db.query(BookModel).all()


@router.get("/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=Book)
def create_book(book: CreateBook, db: Session = Depends(get_db)):
    db_book = BookModel(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.put("/{book_id}", response_model=Book)
def update_book(book_id: int, book_data: CreateBook, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in book_data.dict().items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()

