from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./bookstore.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
logger.debug(f"Engine {DATABASE_URL}")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
logger.debug(f"Session local: {SessionLocal}")


class Base(DeclarativeBase):
    pass