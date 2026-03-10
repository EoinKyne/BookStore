from uuid import UUID
from BookStore.app.schemas.create_book import CreateBook


class Book(CreateBook):
    id: UUID
