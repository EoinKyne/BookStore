from fastapi import APIRouter, HTTPException
from BookStore.app.schemas.book import Book
from BookStore.app.schemas.create_book import CreateBook
from typing import List

router = APIRouter()

books_db = []
book_id = 1


@router.get("/", response_model=list[Book])
def get_books():
    return books_db


@router.get("/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in books_db:
        if book["id"] == book_id:
            return Book
    raise HTTPException(status_code=404, detail="Book not found")


@router.post("/", response_model=Book)
def create_book(book: CreateBook):
    global book_id
    new_book = book.dict()
    new_book["id"] = book_id
    book_id += 1
    books_db.append(new_book)
    return new_book

