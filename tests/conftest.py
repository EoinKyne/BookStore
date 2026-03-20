import logging
import os
import subprocess
import sys
import time

os.environ["ENV_FILE"] = ".env.test"

import pytest
import requests
from playwright.sync_api import APIRequestContext
from sqlalchemy import create_engine, text, inspect, select
from sqlalchemy.orm import sessionmaker

from BookStore.app.auth.auth import get_password_hash
from BookStore.app.database.database import Base
from BookStore.app.dependencies.db_dependencies import get_db
from BookStore.app.main import app
from BookStore.app.models.model import Role as UserRole
from BookStore.app.models.model import User as UserModel
from BookStore.app.core.config import Settings

logger = logging.getLogger(__name__)


BASE_URL = "http://127.0.0.1:8000"


test_settings = Settings(_env_file=".env.test")
DATABASE_URL = test_settings.database_url
logger.info(DATABASE_URL)

TEST_ENGINE = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
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
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def start_fastapi():
    logger.info("Start test")
    env = os.environ.copy()

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
        env=env,
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
def api_request_admin(playwright) -> APIRequestContext:
    logger.debug("Execute API Request")
    request = playwright.request.new_context(base_url=BASE_URL)

    login = request.post(
        "/auth/login/form",
        form={
            "username": "admin",
            "password": "test_pass_1",
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


@pytest.fixture(scope="session")
def add_contributor_user_for_test():
    logger.debug("Add contributor user for testing")

    db = TestingSessionLocal()
    try:
        uname = "bookcontributor"
        stmt = select(UserModel).where(UserModel.username == uname)

        result = db.execute(stmt).scalars().unique().one_or_none()

        if not result:
            hash_pwd = get_password_hash("test_contrib_pass")
            roles = (
                db.query(UserRole).filter(UserRole.name == "Contributor").first()
            )
            packaged_user = UserModel(
                roles=[roles],
                username="bookcontributor",
                password=hash_pwd,
                is_active=True,
            )
            db.add(packaged_user)
            db.commit()
    finally:
        db.close()


@pytest.fixture
def api_request_contributor(playwright, add_contributor_user_for_test) -> APIRequestContext:
    logger.debug("Execute contributor API Request")

    request = playwright.request.new_context(base_url=BASE_URL)

    login = request.post(
        "/auth/login/form",
        form={
            "username": "bookcontributor",
            "password": "test_contrib_pass",
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


@pytest.fixture(scope="session", autouse=True)
def cleanup_database():
    logger.info("Cleaning up...")
    yield

    assert "test" in str(TEST_ENGINE.url), "Incorrect Database"
    with TEST_ENGINE.begin() as conn:
        inspector = inspect(conn)
        tables = inspector.get_table_names()

        if tables:
            truncate = "TRUNCATE TABLE {} RESTART IDENTITY CASCADE;".format(", ".join(tables))

            conn.execute(text(truncate))


@pytest.fixture
def db_session():
    connection = TEST_ENGINE.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()