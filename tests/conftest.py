import subprocess
import time
import sys
import pytest
import requests
from playwright.sync_api import APIRequestContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BookStore.app.database.database import Base
from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.main import app
import logging

logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"

TEST_ENGINE = create_engine(
    "sqlite:///./testbookstore.db",
    connect_args={"check_same_thread": False}
)
logger.debug(f"Test engine: {TEST_ENGINE}")

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TEST_ENGINE
)
logger.debug(f"Testing Session local: {TestingSessionLocal}")

Base.metadata.create_all(bind=TEST_ENGINE)


def override_get_db():
    logger.debug("Overriding db ")
    db = TestingSessionLocal()
    logger.debug(f"Db: {db}")
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def start_fastapi():
    logger.info("Start test")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "BookStore.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,  # windows-safe
    )

    timeout = 100
    start_time = time.time()

    while True:
        try:
            requests.get(f"{BASE_URL}/docs")
            break
        except requests.exceptions.ConnectionError:
            if time.time() - start_time > timeout:
                process.terminate()
                raise RuntimeError("Fastapi did not start in time")
            time.sleep(0.2)
    yield

    process.terminate()
    process.wait()


@pytest.fixture
def api_request_authorized(playwright) -> APIRequestContext:
    logger.debug("Execute API Request")
    request = playwright.request.new_context(base_url=BASE_URL)

    login = request.post(
        "/auth/login/form",
        form={
            "username": "admin",
            "password": "admin123",
        },
    )
    token = login.json()["access_token"]
    request_context = playwright.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={
            "Authorization": f"Bearer {token}"
        },
    )
    yield request_context
    request_context.dispose()


@pytest.fixture
def api_request_not_authorized(playwright) -> APIRequestContext:
    logger.debug("Execute not authorized API Request")
    request = playwright.request.new_context(base_url=BASE_URL)

    request_context = playwright.request.new_context(
        base_url=BASE_URL
    )
    yield request_context
    request_context.dispose()


@pytest.fixture(autouse=True)
def db_transaction():
    logger.info("Rollback db after test")
    connection = TEST_ENGINE.connect()
    db_transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)
    app.dependency_overrides[get_db] = lambda: session

    yield

    #session.close()
    db_transaction.rollback()
    connection.close()



