from BookStore.app.routes import books
import logging
from BookStore.app.core.logging_config import setup_logging
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi import Request, FastAPI

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Bookstore Application")
    yield
    logger.info("Application shutting down")
app = FastAPI(title="Bookstore", lifespan=lifespan)
app.include_router(books.router, prefix="/books", tags=["Books"])


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception",
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )


#@app.middleware("http")
#def log_requests(request: Request, call_next):
#    start_time = time.time()
#    response = call_next(request)
#    duration = round((time.time() - start_time) * 1000, 2)

#    logger.info(
#        "HTTP request",
#        extra={
#            "method": request.method,
#            "path": request.url.path,
#            "status_code": response.status_code,
#            "duration_ms": duration,
#        }
#    )