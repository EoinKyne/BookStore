from fastapi import FastAPI
from BookStore.app.routes import books
from BookStore.app.database.database import engine
from BookStore.app.models.model import Base

app = FastAPI(title="Bookstore")
app.include_router(books.router, prefix="/books", tags=["Books"])
Base.metadata.create_all(bind=engine)
