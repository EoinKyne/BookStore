import subprocess
import time
import sys
import pytest
import requests
from playwright.sync_api import APIRequestContext

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def start_fastapi():
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
def api_request(playwright) -> APIRequestContext:
    request_context = playwright.request.new_context(
        base_url=BASE_URL
    )
    yield request_context
    request_context.dispose()
