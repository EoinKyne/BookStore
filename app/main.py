from fastapi import FastAPI
from BookStore.app.routes import books

app = FastAPI(title="Bookstore")
app.include_router(books.router, prefix="/books", tags=["Books"])